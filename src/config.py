import os
import logging
from dotenv import load_dotenv

# Load environment variables - I always put this at the top
load_dotenv()

# Configuration class - I prefer this over scattered constants everywhere
class Config:
    # API credentials - NEVER hardcode these!
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
    TESTNET = os.getenv('TESTNET', 'true').lower() == 'true'  # Default to testnet for safety
    
    # Logging setup - learned to make this configurable after debugging nightmares
    LOG_LEVEL = logging.INFO  # Change to DEBUG when things go wrong
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'bot.log'  # All the important stuff goes here
    
    # Trading limits - safety first! These saved me from fat finger errors
    MIN_QUANTITY = 0.001  # Binance minimum for most pairs
    MAX_QUANTITY = 1000   # My personal risk limit
    MIN_PRICE = 0.01      # Sanity check for price inputs
    
    # Grid trading defaults - these work well for BTC in my experience
    DEFAULT_GRID_LEVELS = 10     # Sweet spot between coverage and complexity
    DEFAULT_GRID_SPREAD = 0.01   # 1% - conservative but profitable
    
    # TWAP defaults - based on my testing with different market conditions
    DEFAULT_TWAP_DURATION = 300  # 5 minutes - good balance for most orders
    DEFAULT_TWAP_INTERVALS = 10  # 10 chunks - not too aggressive, not too slow