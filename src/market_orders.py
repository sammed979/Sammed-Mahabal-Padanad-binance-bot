from binance.client import Client
from binance.exceptions import BinanceAPIException
from logger import bot_logger
from validator import OrderValidator

# Market orders are the simplest but most important - get these right first!
class MarketOrderManager:
    def __init__(self, client: Client):
        self.client = client
        self.validator = OrderValidator(client)
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """Place a market order - I prefer this over limit orders for quick entries"""
        try:
            # Quick validation - learned to do this after some embarrassing API errors
            if not symbol or not side or quantity <= 0:
                error_msg = "Invalid parameters - caught this before hitting the API!"
                bot_logger.log_error(error_msg)
                return {'success': False, 'error': error_msg}
            
            # Log order attempt
            bot_logger.log_order('MARKET', symbol, quantity, None, 'PLACING')
            
            # Demo mode - my safety net during development
            if self.client is None:
                import random  # Using random IDs to simulate real order IDs
                demo_order_id = random.randint(10000000, 99999999)  # Binance-like order ID format
                bot_logger.log_order('MARKET', symbol, quantity, None, 'PLACED (DEMO)')
                bot_logger.log_execution(demo_order_id, symbol, quantity, 'MARKET_PRICE (DEMO)')
                
                return {
                    'success': True,
                    'order_id': demo_order_id,
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'type': 'MARKET',
                    'status': 'FILLED (DEMO)'
                }
            
            # Real API call
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='MARKET',
                quantity=quantity
            )
            
            # Log successful order
            bot_logger.log_order('MARKET', symbol, quantity, None, 'PLACED')
            bot_logger.log_execution(order['orderId'], symbol, quantity, 'MARKET_PRICE')
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'type': 'MARKET',
                'status': order['status']
            }
            
        except BinanceAPIException as e:
            error_msg = f"Binance API error: {e.message}"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Unexpected error placing market order"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
    
    def get_market_price(self, symbol: str) -> float:
        """Get current market price - useful for calculating order values"""
        try:
            if self.client is None:
                # Realistic demo prices based on current market levels (Oct 2024)
                demo_prices = {'BTCUSDT': 45000.0, 'ETHUSDT': 3000.0, 'ADAUSDT': 0.5}
                return demo_prices.get(symbol.upper(), 100.0)  # Default fallback price
                
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            return float(ticker['price'])
        except Exception as e:
            bot_logger.log_error(f"Failed to get market price for {symbol}", e)
            return None