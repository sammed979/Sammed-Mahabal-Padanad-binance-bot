import time
import threading
from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import bot_logger
from validator import OrderValidator
from config import Config

# TWAP (Time-Weighted Average Price) - great for large orders
# I use this when I need to buy/sell big amounts without moving the market too much
class TWAPOrderManager:
    def __init__(self, client: Client):
        self.client = client
        self.validator = OrderValidator(client)
        self.active_twaps = {}
    
    def execute_twap_order(self, symbol: str, side: str, total_quantity: float, duration_seconds: int = None, intervals: int = None) -> dict:
        """
        Execute TWAP - my go-to strategy for large orders
        
        I learned this technique from institutional traders - it really helps reduce slippage
        when you're moving serious size. The key is finding the right interval timing.
        """
        try:
            # Use sensible defaults if not specified
            duration_seconds = duration_seconds or Config.DEFAULT_TWAP_DURATION  # 5 minutes default
            intervals = intervals or Config.DEFAULT_TWAP_INTERVALS  # 10 chunks default
            
            # Validate inputs
            is_valid, errors = self.validator.validate_order(symbol, side, 'MARKET', total_quantity)
            if not is_valid:
                error_msg = f"TWAP validation failed: {', '.join(errors)}"
                bot_logger.log_error(error_msg)
                return {'success': False, 'error': error_msg}
            
            if intervals <= 0 or duration_seconds <= 0:
                error_msg = "Invalid TWAP parameters: intervals and duration must be positive"
                bot_logger.log_error(error_msg)
                return {'success': False, 'error': error_msg}
            
            # Calculate order parameters - simple math but crucial to get right
            chunk_size = total_quantity / intervals  # Size of each individual order
            interval_delay = duration_seconds / intervals  # Time between orders
            
            bot_logger.log_order('TWAP_START', symbol, total_quantity, 
                               f"Chunks:{intervals}, Duration:{duration_seconds}s", 'STARTING')
            
            # Generate unique TWAP ID - timestamp makes it easy to track
            twap_id = f"{symbol}_{int(time.time())}"
            
            # Store TWAP info - I track everything for later analysis
            self.active_twaps[twap_id] = {
                'symbol': symbol,
                'side': side,
                'total_quantity': total_quantity,
                'chunk_size': chunk_size,
                'intervals': intervals,
                'interval_delay': interval_delay,
                'executed_chunks': 0,  # Progress tracking
                'executed_quantity': 0,  # Running total
                'orders': [],  # All individual orders
                'status': 'ACTIVE'  # State management
            }
            
            # Start TWAP execution in separate thread
            twap_thread = threading.Thread(
                target=self._execute_twap_chunks,
                args=(twap_id,)
            )
            twap_thread.daemon = True
            twap_thread.start()
            
            return {
                'success': True,
                'twap_id': twap_id,
                'symbol': symbol,
                'side': side,
                'total_quantity': total_quantity,
                'chunk_size': chunk_size,
                'intervals': intervals,
                'duration_seconds': duration_seconds,
                'type': 'TWAP'
            }
            
        except Exception as e:
            error_msg = f"Failed to start TWAP order"
            bot_logger.log_error(error_msg, e)
            return {'success': False, 'error': error_msg}
    
    def _execute_twap_chunks(self, twap_id: str):
        """Execute TWAP chunks in separate thread"""
        twap_info = self.active_twaps[twap_id]
        
        try:
            for i in range(twap_info['intervals']):
                if twap_info['status'] != 'ACTIVE':
                    break
                
                # Calculate chunk quantity (handle remainder in last chunk)
                if i == twap_info['intervals'] - 1:
                    chunk_qty = twap_info['total_quantity'] - twap_info['executed_quantity']
                else:
                    chunk_qty = twap_info['chunk_size']
                
                # Place market order for chunk
                try:
                    order = self.client.futures_create_order(
                        symbol=twap_info['symbol'],
                        side=twap_info['side'],
                        type='MARKET',
                        quantity=chunk_qty
                    )
                    
                    # Update TWAP info
                    twap_info['executed_chunks'] += 1
                    twap_info['executed_quantity'] += chunk_qty
                    twap_info['orders'].append(order)
                    
                    bot_logger.log_order('TWAP_CHUNK', twap_info['symbol'], chunk_qty, 
                                       f"Chunk {i+1}/{twap_info['intervals']}", 'EXECUTED')
                    
                except BinanceAPIException as e:
                    bot_logger.log_error(f"TWAP chunk {i+1} failed: {e.message}", e)
                    continue
                
                # Wait for next interval (except for last chunk)
                if i < twap_info['intervals'] - 1:
                    time.sleep(twap_info['interval_delay'])
            
            # Mark TWAP as completed
            twap_info['status'] = 'COMPLETED'
            bot_logger.log_order('TWAP_COMPLETE', twap_info['symbol'], twap_info['executed_quantity'], 
                               f"Executed {twap_info['executed_chunks']}/{twap_info['intervals']} chunks", 'COMPLETED')
            
        except Exception as e:
            twap_info['status'] = 'FAILED'
            bot_logger.log_error(f"TWAP execution failed for {twap_id}", e)
    
    def cancel_twap(self, twap_id: str) -> dict:
        """Cancel active TWAP order"""
        if twap_id not in self.active_twaps:
            return {'success': False, 'error': 'TWAP ID not found'}
        
        self.active_twaps[twap_id]['status'] = 'CANCELLED'
        bot_logger.logger.info(f"TWAP_CANCELLED: {twap_id}")
        
        return {'success': True, 'twap_id': twap_id, 'status': 'CANCELLED'}
    
    def get_twap_status(self, twap_id: str) -> dict:
        """Get TWAP execution status"""
        if twap_id not in self.active_twaps:
            return {'success': False, 'error': 'TWAP ID not found'}
        
        return {'success': True, 'twap_info': self.active_twaps[twap_id]}