import logging
import os
from datetime import datetime
from config import Config

# Custom logging class - I got tired of print statements everywhere!
# This makes debugging so much easier, especially when things go wrong at 2 AM
class BotLogger:
    def __init__(self):
        self.logger = logging.getLogger('BinanceBot')
        self.logger.setLevel(Config.LOG_LEVEL)
        
        # Prevent duplicate handlers - learned this the hard way!
        if not self.logger.handlers:
            # File handler - all logs go to file for later analysis
            file_handler = logging.FileHandler(Config.LOG_FILE)
            file_handler.setLevel(Config.LOG_LEVEL)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(Config.LOG_LEVEL)
            
            # Formatter
            formatter = logging.Formatter(Config.LOG_FORMAT)
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_order(self, order_type, symbol, quantity, price=None, status='PENDING'):
        # Custom order logging format - makes it easy to grep through logs later
        self.logger.info(f"ORDER: {order_type} | {symbol} | Qty: {quantity} | Price: {price} | Status: {status}")
    
    def log_error(self, error_msg, exception=None):
        # Error logging with optional exception details - saved me hours of debugging
        if exception:
            self.logger.error(f"ERROR: {error_msg} | Exception: {str(exception)}")
        else:
            self.logger.error(f"ERROR: {error_msg}")
    
    def log_execution(self, order_id, symbol, executed_qty, avg_price):
        # Track executions for P&L analysis - this data is gold for strategy optimization
        self.logger.info(f"EXECUTION: OrderID: {order_id} | {symbol} | Executed: {executed_qty} | Avg Price: {avg_price}")

bot_logger = BotLogger()