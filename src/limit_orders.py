from binance.client import Client
from binance.exceptions import BinanceAPIException
from logger import bot_logger
from validator import OrderValidator

class LimitOrderManager:
    def __init__(self, client: Client):
        self.client = client
        self.validator = OrderValidator(client)
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, time_in_force: str = 'GTC') -> dict:
        """Place a limit order"""
        try:
            # Basic validation
            if not symbol or not side or quantity <= 0 or price <= 0:
                error_msg = "Invalid parameters"
                bot_logger.log_error(error_msg)
                return {'success': False, 'error': error_msg}
            
            # Log order attempt
            bot_logger.log_order('LIMIT', symbol, quantity, price, 'PLACING')
            
            # Demo mode
            if self.client is None:
                import random
                demo_order_id = random.randint(10000000, 99999999)
                bot_logger.log_order('LIMIT', symbol, quantity, price, 'PLACED (DEMO)')
                
                return {
                    'success': True,
                    'order_id': demo_order_id,
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'type': 'LIMIT',
                    'status': 'NEW (DEMO)',
                    'time_in_force': time_in_force
                }
            
            # Real API call
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='LIMIT',
                quantity=quantity,
                price=price,
                timeInForce=time_in_force
            )
            
            # Log successful order
            bot_logger.log_order('LIMIT', symbol, quantity, price, 'PLACED')
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'type': 'LIMIT',
                'status': order['status'],
                'time_in_force': time_in_force
            }
            
        except BinanceAPIException as e:
            error_msg = f"Binance API error: {e.message}"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Unexpected error placing limit order"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
    
    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel a limit order"""
        try:
            result = self.client.futures_cancel_order(symbol=symbol.upper(), orderId=order_id)
            bot_logger.logger.info(f"CANCELLED: OrderID: {order_id} | {symbol}")
            return {'success': True, 'order_id': order_id, 'status': 'CANCELLED'}
        except Exception as e:
            error_msg = f"Failed to cancel order {order_id}"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
    
    def get_open_orders(self, symbol: str = None) -> list:
        """Get all open orders"""
        try:
            if self.client is None:
                # Demo orders
                return [{
                    'orderId': 12345678,
                    'symbol': 'BTCUSDT',
                    'side': 'BUY',
                    'origQty': '0.001',
                    'price': '44000.0',
                    'status': 'NEW (DEMO)'
                }]
                
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol.upper())
            else:
                orders = self.client.futures_get_open_orders()
            return orders
        except Exception as e:
            bot_logger.log_error("Failed to get open orders", e)
            return []