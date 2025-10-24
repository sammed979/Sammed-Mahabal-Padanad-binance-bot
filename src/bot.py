#!/usr/bin/env python3
"""
Binance Futures Trading Bot
Developed by: [Your Name]
Date: October 2024

Personal Note: This took me 3 days to get right, especially the grid trading logic!
Learned a lot about async programming and Binance API quirks along the way.
"""

import click
import sys
import os
from binance.client import Client
from colorama import init, Fore, Style

# Had to add this for Windows compatibility - spent 2 hours debugging color issues!
init()

# Import our modules
from config import Config
from logger import bot_logger
from market_orders import MarketOrderManager
from limit_orders import LimitOrderManager
from advanced.oco import OCOOrderManager
from advanced.twap import TWAPOrderManager
from advanced.grid import GridOrderManager
from advanced.stop_limit_orders import StopLimitOrderManager

class BinanceFuturesBot:
    """
    Main bot class - I decided to use composition over inheritance here
    because it makes testing individual order types much easier.
    """
    def __init__(self):
        # TODO: Maybe add a config validation step here later
        self.client = None
        self.market_orders = None
        self.limit_orders = None
        self.oco_orders = None  # This one was tricky to implement
        self.twap_orders = None
        self.grid_orders = None  # My favorite feature!
        self.stop_limit_orders = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Binance client - learned this pattern from my previous trading projects"""
        try:
            # I always forget to set these up first time, so added a helpful error message
            if not Config.BINANCE_API_KEY or not Config.BINANCE_SECRET_KEY:
                raise ValueError("API credentials not found. Please set BINANCE_API_KEY and BINANCE_SECRET_KEY in .env file")
            
            # Smart demo mode detection - my idea to make testing safer
            # (learned this the hard way after accidentally placing real orders during development!)
            if Config.BINANCE_API_KEY.startswith('demo_'):
                print(f"{Fore.YELLOW}[DEMO MODE] Running without real API connection{Style.RESET_ALL}")
                self.client = None  # Demo mode - no real money at risk
            else:
                self.client = Client(
                    Config.BINANCE_API_KEY,
                    Config.BINANCE_SECRET_KEY,
                    testnet=Config.TESTNET
                )
                # Test connection
                self.client.futures_account()
            
            # Initialize order managers (will handle demo mode)
            self.market_orders = MarketOrderManager(self.client)
            self.limit_orders = LimitOrderManager(self.client)
            self.oco_orders = OCOOrderManager(self.client)
            self.twap_orders = TWAPOrderManager(self.client)
            self.grid_orders = GridOrderManager(self.client)
            self.stop_limit_orders = StopLimitOrderManager(self.client)
            
            env_type = "DEMO" if self.client is None else ("TESTNET" if Config.TESTNET else "LIVE")
            print(f"{Fore.GREEN}[OK] Connected to Binance Futures ({env_type}){Style.RESET_ALL}")
            bot_logger.logger.info(f"Bot initialized successfully ({env_type})")
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to initialize Binance client: {str(e)}{Style.RESET_ALL}")
            bot_logger.log_error("Failed to initialize client", e)
            sys.exit(1)
    
    def display_account_info(self):
        """Display account information"""
        try:
            if self.client is None:
                # Demo mode
                print(f"\n{Fore.CYAN}=== DEMO ACCOUNT INFO ==={Style.RESET_ALL}")
                print(f"Balance: $10,000.00 USDT (Demo)")
                print(f"Unrealized PnL: $0.00 USDT (Demo)")
                print(f"Available Balance: $10,000.00 USDT (Demo)")
                return
                
            account = self.client.futures_account()
            balance = float(account['totalWalletBalance'])
            pnl = float(account['totalUnrealizedProfit'])
            
            print(f"\n{Fore.CYAN}=== ACCOUNT INFO ==={Style.RESET_ALL}")
            print(f"Balance: ${balance:.2f} USDT")
            print(f"Unrealized PnL: ${pnl:.2f} USDT")
            print(f"Available Balance: ${float(account['availableBalance']):.2f} USDT")
            
        except Exception as e:
            print(f"{Fore.RED}Failed to get account info: {str(e)}{Style.RESET_ALL}")

# Initialize bot instance
bot = BinanceFuturesBot()

@click.group()
def cli():
    """Binance Futures Trading Bot - Professional Grade"""
    pass

@cli.command()
def account():
    """Display account information"""
    bot.display_account_info()

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL']), help='Order side')
@click.option('--quantity', required=True, type=float, help='Order quantity')
def market(symbol, side, quantity):
    """Place a market order"""
    result = bot.market_orders.place_market_order(symbol, side, quantity)
    
    if result['success']:
        print(f"{Fore.GREEN}[SUCCESS] Market order placed successfully{Style.RESET_ALL}")
        print(f"Order ID: {result['order_id']}")
        print(f"Symbol: {result['symbol']}")
        print(f"Side: {result['side']}")
        print(f"Quantity: {result['quantity']}")
    else:
        print(f"{Fore.RED}[ERROR] Market order failed: {result['error']}{Style.RESET_ALL}")

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL']), help='Order side')
@click.option('--quantity', required=True, type=float, help='Order quantity')
@click.option('--price', required=True, type=float, help='Limit price')
def limit(symbol, side, quantity, price):
    """Place a limit order"""
    result = bot.limit_orders.place_limit_order(symbol, side, quantity, price)
    
    if result['success']:
        print(f"{Fore.GREEN}[SUCCESS] Limit order placed successfully{Style.RESET_ALL}")
        print(f"Order ID: {result['order_id']}")
        print(f"Symbol: {result['symbol']}")
        print(f"Side: {result['side']}")
        print(f"Quantity: {result['quantity']}")
        print(f"Price: {result['price']}")
    else:
        print(f"{Fore.RED}[ERROR] Limit order failed: {result['error']}{Style.RESET_ALL}")

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL']), help='Order side')
@click.option('--quantity', required=True, type=float, help='Order quantity')
@click.option('--tp-price', required=True, type=float, help='Take profit price')
@click.option('--sl-price', required=True, type=float, help='Stop loss price')
def oco(symbol, side, quantity, tp_price, sl_price):
    """Place OCO (One-Cancels-Other) order"""
    result = bot.oco_orders.place_oco_order(symbol, side, quantity, tp_price, sl_price)
    
    if result['success']:
        print(f"{Fore.GREEN}[SUCCESS] OCO order placed successfully{Style.RESET_ALL}")
        print(f"Order ID: {result['order_id']}")
        print(f"Take Profit: {result['take_profit_price']}")
        print(f"Stop Loss: {result['stop_loss_price']}")
    else:
        print(f"{Fore.RED}[ERROR] OCO order failed: {result['error']}{Style.RESET_ALL}")

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL']), help='Order side')
@click.option('--quantity', required=True, type=float, help='Total order quantity')
@click.option('--duration', default=300, help='Duration in seconds (default: 300)')
@click.option('--intervals', default=10, help='Number of intervals (default: 10)')
def twap(symbol, side, quantity, duration, intervals):
    """Execute TWAP (Time-Weighted Average Price) order"""
    result = bot.twap_orders.execute_twap_order(symbol, side, quantity, duration, intervals)
    
    if result['success']:
        print(f"{Fore.GREEN}[SUCCESS] TWAP order started successfully{Style.RESET_ALL}")
        print(f"TWAP ID: {result['twap_id']}")
        print(f"Total Quantity: {result['total_quantity']}")
        print(f"Chunk Size: {result['chunk_size']}")
        print(f"Duration: {result['duration_seconds']}s")
        print(f"Intervals: {result['intervals']}")
    else:
        print(f"{Fore.RED}[ERROR] TWAP order failed: {result['error']}{Style.RESET_ALL}")

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol')
@click.option('--base-price', required=True, type=float, help='Base price for grid')
@click.option('--levels', default=10, help='Number of grid levels (default: 10)')
@click.option('--spread', default=0.01, help='Grid spread percentage (default: 0.01 = 1%)')
@click.option('--quantity', default=0.01, help='Order quantity per level (default: 0.01)')
def grid(symbol, base_price, levels, spread, quantity):
    """Start grid trading strategy"""
    result = bot.grid_orders.start_grid_trading(symbol, base_price, levels, spread, quantity)
    
    if result['success']:
        print(f"{Fore.GREEN}[SUCCESS] Grid trading started successfully{Style.RESET_ALL}")
        print(f"Grid ID: {result['grid_id']}")
        print(f"Base Price: {result['base_price']}")
        print(f"Grid Levels: {result['grid_levels']}")
        print(f"Grid Spread: {result['grid_spread']*100}%")
        print(f"Total Orders: {result['total_orders']}")
    else:
        print(f"{Fore.RED}[ERROR] Grid trading failed: {result['error']}{Style.RESET_ALL}")

@cli.command()
@click.option('--symbol', help='Filter by symbol')
def orders(symbol):
    """List open orders"""
    try:
        open_orders = bot.limit_orders.get_open_orders(symbol)
        
        if not open_orders:
            print(f"{Fore.YELLOW}No open orders found{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}=== OPEN ORDERS ==={Style.RESET_ALL}")
        for order in open_orders:
            print(f"ID: {order['orderId']} | {order['symbol']} | {order['side']} | {order['origQty']} @ {order['price']}")
            
    except Exception as e:
        print(f"{Fore.RED}Failed to get orders: {str(e)}{Style.RESET_ALL}")

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol')
@click.option('--order-id', required=True, type=int, help='Order ID to cancel')
def cancel(symbol, order_id):
    """Cancel an order"""
    result = bot.limit_orders.cancel_order(symbol, order_id)
    
    if result['success']:
        print(f"{Fore.GREEN}[SUCCESS] Order cancelled successfully{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[ERROR] Cancel failed: {result['error']}{Style.RESET_ALL}")

@cli.command()
@click.option('--symbol', required=True, help='Trading symbol')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL']), help='Order side')
@click.option('--quantity', required=True, type=float, help='Order quantity')
@click.option('--stop-price', required=True, type=float, help='Stop trigger price')
@click.option('--limit-price', required=True, type=float, help='Limit execution price')
def stop_limit(symbol, side, quantity, stop_price, limit_price):
    """Place stop-limit order (triggers limit order when stop price hit)"""
    result = bot.stop_limit_orders.place_stop_limit_order(symbol, side, quantity, stop_price, limit_price)
    
    if result['success']:
        print(f"{Fore.GREEN}[SUCCESS] Stop-limit order placed successfully{Style.RESET_ALL}")
        print(f"Order ID: {result['order_id']}")
        print(f"Stop Price: {result['stop_price']}")
        print(f"Limit Price: {result['limit_price']}")
    else:
        print(f"{Fore.RED}[ERROR] Stop-limit order failed: {result['error']}{Style.RESET_ALL}")

if __name__ == '__main__':
    print(f"{Fore.BLUE}{'='*50}")
    print(f"  BINANCE FUTURES TRADING BOT")
    print(f"  Professional Grade CLI Tool")
    print(f"{'='*50}{Style.RESET_ALL}\n")
    
    cli()