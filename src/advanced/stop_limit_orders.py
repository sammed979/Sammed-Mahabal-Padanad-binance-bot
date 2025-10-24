from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import bot_logger
from validator import OrderValidator

class StopLimitOrderManager:
    def __init__(self, client: Client):
        self.client = client
        self.validator = OrderValidator(client)
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, stop_price: float, limit_price: float) -> dict:
        """
        Place a stop-limit order
        Triggers a limit order when stop price is hit
        """
        try:
            # Basic validation
            if not symbol or not side or quantity <= 0 or stop_price <= 0 or limit_price <= 0:
                error_msg = "Invalid stop-limit parameters"
                bot_logger.log_error(error_msg)
                return {'success': False, 'error': error_msg}
            
            bot_logger.log_order('STOP_LIMIT', symbol, quantity, f"Stop:{stop_price}, Limit:{limit_price}", 'PLACING')
            
            # Demo mode
            if self.client is None:
                import random
                demo_order_id = random.randint(10000000, 99999999)
                bot_logger.log_order('STOP_LIMIT', symbol, quantity, f"Stop:{stop_price}, Limit:{limit_price}", 'PLACED (DEMO)')
                
                return {
                    'success': True,
                    'order_id': demo_order_id,
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'stop_price': stop_price,
                    'limit_price': limit_price,
                    'type': 'STOP_LIMIT',
                    'status': 'NEW (DEMO)'
                }
            
            # Real API call
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='STOP',
                quantity=quantity,
                stopPrice=stop_price,
                price=limit_price,
                timeInForce='GTC'
            )
            
            bot_logger.log_order('STOP_LIMIT', symbol, quantity, f"Stop:{stop_price}, Limit:{limit_price}", 'PLACED')
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'stop_price': stop_price,
                'limit_price': limit_price,
                'type': 'STOP_LIMIT',
                'status': order['status']
            }
            
        except BinanceAPIException as e:
            error_msg = f"Binance API error in stop-limit: {e.message}"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Unexpected error placing stop-limit order"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}