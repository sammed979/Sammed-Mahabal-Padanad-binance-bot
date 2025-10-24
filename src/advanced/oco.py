from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import bot_logger
from validator import OrderValidator

class OCOOrderManager:
    def __init__(self, client: Client):
        self.client = client
        self.validator = OrderValidator(client)
    
    def place_oco_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float, stop_limit_price: float = None) -> dict:
        """
        Place OCO (One-Cancels-Other) order
        - Take profit at 'price'
        - Stop loss at 'stop_price' (market) or 'stop_limit_price' (limit)
        """
        try:
            # Validate basic parameters
            is_valid, errors = self.validator.validate_order(symbol, side, 'LIMIT', quantity, price)
            if not is_valid:
                error_msg = f"OCO validation failed: {', '.join(errors)}"
                bot_logger.log_error(error_msg)
                return {'success': False, 'error': error_msg}
            
            # Validate stop price
            if not self.validator.validate_price(stop_price):
                error_msg = f"Invalid stop price: {stop_price}"
                bot_logger.log_error(error_msg)
                return {'success': False, 'error': error_msg}
            
            bot_logger.log_order('OCO', symbol, quantity, f"TP:{price}, SL:{stop_price}", 'PLACING')
            
            # Determine OCO parameters
            oco_params = {
                'symbol': symbol.upper(),
                'side': side.upper(),
                'quantity': quantity,
                'price': price,
                'stopPrice': stop_price,
                'timeInForce': 'GTC'
            }
            
            # Add stop limit price if provided
            if stop_limit_price:
                oco_params['stopLimitPrice'] = stop_limit_price
                oco_params['stopLimitTimeInForce'] = 'GTC'
            
            # Demo mode
            if self.client is None:
                import random
                demo_order_id = random.randint(10000000, 99999999)
                bot_logger.log_order('OCO', symbol, quantity, f"TP:{price}, SL:{stop_price}", 'PLACED (DEMO)')
                
                return {
                    'success': True,
                    'order_id': demo_order_id,
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'take_profit_price': price,
                    'stop_loss_price': stop_price,
                    'stop_limit_price': stop_limit_price,
                    'type': 'OCO',
                    'status': 'NEW (DEMO)'
                }
            
            # Place OCO order
            order = self.client.futures_create_order(
                symbol=oco_params['symbol'],
                side=oco_params['side'],
                type='TAKE_PROFIT',
                quantity=oco_params['quantity'],
                price=oco_params['price'],
                stopPrice=oco_params['stopPrice'],
                timeInForce=oco_params['timeInForce']
            )
            
            bot_logger.log_order('OCO', symbol, quantity, f"TP:{price}, SL:{stop_price}", 'PLACED')
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'take_profit_price': price,
                'stop_loss_price': stop_price,
                'stop_limit_price': stop_limit_price,
                'type': 'OCO',
                'status': order['status']
            }
            
        except BinanceAPIException as e:
            error_msg = f"Binance API error in OCO: {e.message}"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Unexpected error placing OCO order"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
    
    def place_bracket_order(self, symbol: str, side: str, quantity: float, entry_price: float, take_profit: float, stop_loss: float) -> dict:
        """
        Place a bracket order (entry + OCO)
        """
        try:
            # First place entry order
            entry_order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='LIMIT',
                quantity=quantity,
                price=entry_price,
                timeInForce='GTC'
            )
            
            bot_logger.log_order('BRACKET_ENTRY', symbol, quantity, entry_price, 'PLACED')
            
            # Then place OCO for exit
            opposite_side = 'SELL' if side.upper() == 'BUY' else 'BUY'
            oco_result = self.place_oco_order(symbol, opposite_side, quantity, take_profit, stop_loss)
            
            return {
                'success': True,
                'entry_order_id': entry_order['orderId'],
                'oco_result': oco_result,
                'type': 'BRACKET'
            }
            
        except Exception as e:
            error_msg = f"Failed to place bracket order"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}