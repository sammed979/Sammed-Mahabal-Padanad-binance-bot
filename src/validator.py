import re
from binance.client import Client
from config import Config
from logger import bot_logger

class OrderValidator:
    def __init__(self, client: Client):
        self.client = client
        self.exchange_info = None
        self._load_exchange_info()
    
    def _load_exchange_info(self):
        try:
            self.exchange_info = self.client.futures_exchange_info()
        except Exception as e:
            bot_logger.log_error("Failed to load exchange info", e)
    
    def validate_symbol(self, symbol: str) -> bool:
        if not symbol or not isinstance(symbol, str):
            return False
        
        symbol = symbol.upper()
        if not self.exchange_info:
            return True  # Skip validation if exchange info unavailable
        
        symbols = [s['symbol'] for s in self.exchange_info['symbols']]
        return symbol in symbols
    
    def validate_quantity(self, symbol: str, quantity: float) -> bool:
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return False
        
        if quantity < Config.MIN_QUANTITY or quantity > Config.MAX_QUANTITY:
            return False
        
        return True
    
    def validate_price(self, price: float) -> bool:
        if price is None:
            return True  # Market orders don't need price
        
        if not isinstance(price, (int, float)) or price <= 0:
            return False
        
        return price >= Config.MIN_PRICE
    
    def validate_side(self, side: str) -> bool:
        return side.upper() in ['BUY', 'SELL']
    
    def validate_order_type(self, order_type: str) -> bool:
        valid_types = ['MARKET', 'LIMIT', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET']
        return order_type.upper() in valid_types
    
    def validate_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> tuple:
        errors = []
        
        if not self.validate_symbol(symbol):
            errors.append(f"Invalid symbol: {symbol}")
        
        if not self.validate_side(side):
            errors.append(f"Invalid side: {side}")
        
        if not self.validate_order_type(order_type):
            errors.append(f"Invalid order type: {order_type}")
        
        if not self.validate_quantity(symbol, quantity):
            errors.append(f"Invalid quantity: {quantity}")
        
        if not self.validate_price(price):
            errors.append(f"Invalid price: {price}")
        
        return len(errors) == 0, errors