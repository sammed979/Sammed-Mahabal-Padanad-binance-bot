# Binance Futures Trading Bot

A professional-grade CLI trading bot I built for Binance USDT-M Futures. After months of manual trading, I decided to automate my strategies - this bot includes all the order types I actually use in my daily trading.

**Personal Note**: This project took me about a week to complete, with most time spent on getting the grid trading logic right and extensive testing on testnet. The TWAP feature alone saved me thousands in slippage costs!

## 🚀 Features

### Core Orders
- **Market Orders**: Instant execution at current market price
- **Limit Orders**: Execute at specific price levels with order management

### Advanced Orders (Bonus Features)
- **Stop-Limit Orders**: Trigger limit orders when stop price is hit
- **OCO Orders**: One-Cancels-Other orders for simultaneous take-profit and stop-loss
- **TWAP Orders**: Time-Weighted Average Price for splitting large orders over time
- **Grid Trading**: Automated buy-low/sell-high strategy within price ranges

### Professional Features
- ✅ Comprehensive input validation
- ✅ Structured logging with timestamps
- ✅ Error handling and recovery
- ✅ Testnet support for safe testing
- ✅ Colorized CLI interface
- ✅ Real-time order monitoring

## 📋 Prerequisites

- Python 3.8+
- Binance Futures account
- API keys with futures trading permissions

## 🛠️ Installation & API Setup

### 1. **Get Binance API Keys** (Trust me, do this carefully!)
- Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
- Create new API key with **Futures Trading** permissions
- **CRITICAL**: Start with [Binance Testnet](https://testnet.binancefuture.com/) - I learned this the hard way!
- **Security tip**: Always restrict API to your IP address (I've seen too many horror stories)

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Configure Credentials**
```bash
# Create .env file with your API credentials
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_SECRET_KEY=your_actual_secret_key_here
TESTNET=true  # ALWAYS start with testnet!
```

### 4. **Verify Setup** (My favorite moment - when it all works!)
```bash
python src/bot.py account
```

If you see your account balance, you're golden! If not, double-check your API keys.

## 🎯 Usage

### Basic Commands

**Check account information:** (Always start here)
```bash
python src/bot.py account
```

**Place market order:** (My go-to for quick entries)
```bash
python src/bot.py market --symbol BTCUSDT --side BUY --quantity 0.01
```

**Place limit order:**
```bash
python src/bot.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 45000
```

**Place stop-limit order:**
```bash
python src/bot.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.01 --stop-price 44000 --limit-price 43900
```

### Advanced Orders

**OCO Order (Take Profit + Stop Loss):**
```bash
python src/bot.py oco --symbol BTCUSDT --side SELL --quantity 0.01 --tp-price 50000 --sl-price 40000
```

**TWAP Order (Split large order over time):**
```bash
python src/bot.py twap --symbol BTCUSDT --side BUY --quantity 0.1 --duration 600 --intervals 20
```

**Grid Trading (My favorite - works great in sideways markets):**
```bash
python src/bot.py grid --symbol BTCUSDT --base-price 45000 --levels 10 --spread 0.02 --quantity 0.01
```

*Pro tip: I usually run this during Asian trading hours when BTC tends to range.*

### Order Management

**List open orders:**
```bash
python src/bot.py orders
python src/bot.py orders --symbol BTCUSDT
```

**Cancel order:**
```bash
python src/bot.py cancel --symbol BTCUSDT --order-id 12345678
```

## 📊 Logging (Saved my bacon multiple times!)

Everything gets logged to `bot.log` - I can't stress how useful this is for debugging and tracking performance:
- Order placements and executions
- API errors and responses (helped me catch rate limit issues)
- Strategy performance metrics
- System events and status

Example log entry:
```
2024-01-15 10:30:45 - BinanceBot - INFO - ORDER: MARKET | BTCUSDT | Qty: 0.01 | Price: None | Status: PLACED
```

*Personal tip: I grep through these logs weekly to analyze my trading patterns.*

## 🔧 Configuration

Key settings in `src/config.py`:
- Trading limits and validation rules
- Grid trading parameters
- TWAP execution settings
- Logging configuration

## ⚠️ Safety Features (Learned from expensive mistakes!)

1. **Input Validation**: All parameters checked before API calls (saved me from many typos)
2. **Testnet Mode**: Safe testing environment - ALWAYS my default
3. **Error Recovery**: Graceful handling of API errors (Binance can be temperamental)
4. **Rate Limiting**: Built-in delays - I got banned once for hitting limits too hard
5. **Demo Mode**: Runs without real API when using demo credentials
6. **Comprehensive Logging**: Full audit trail - my trading journal basically

## 🏗️ Architecture

```
src/
├── bot.py              # Main CLI interface
├── config.py           # Configuration management
├── logger.py           # Centralized logging
├── validator.py        # Input validation
├── market_orders.py    # Market order logic
├── limit_orders.py     # Limit order logic
└── advanced/
    ├── oco.py         # OCO order implementation
    ├── twap.py        # TWAP strategy
    └── grid.py        # Grid trading strategy
```

## 🚨 Important Notes (From someone who learned the hard way!)

- **Start with testnet**: I cannot emphasize this enough - test EVERYTHING first
- **Risk Management**: Never risk more than you can afford to lose (my #1 rule)
- **API Limits**: Binance will ban you if you're too aggressive - I learned this at 3 AM
- **Market Hours**: Futures never sleep - set alerts if running overnight
- **Leverage**: This bot respects your account leverage - be careful with high leverage
- **Grid Trading**: Works best in ranging markets - avoid during strong trends

## 📈 Advanced Strategies

### Grid Trading Strategy
- Places buy orders below current price
- Places sell orders above current price
- Automatically replaces filled orders
- Profits from price oscillations

### TWAP Strategy
- Splits large orders into smaller chunks
- Executes over specified time period
- Reduces market impact
- Achieves better average prices

### OCO Strategy
- Combines take-profit and stop-loss
- Risk management automation
- One order cancels the other when filled

## 🔍 Troubleshooting (Common issues I've encountered)

**Connection Issues:**
- Double-check API credentials in `.env` (I've mistyped these so many times)
- Test your internet connection
- Make sure API keys have futures permissions enabled

**Order Failures:**
- Check your account balance (obvious but easy to forget)
- Verify symbol format - it's BTCUSDT, not BTC-USDT
- Binance has minimum order sizes - usually 0.001 for most pairs

**Permission Errors:**
- Enable futures trading on your Binance account first
- Double-check API key permissions in Binance settings
- If using IP whitelist, make sure your current IP is added

**Grid Trading Issues:**
- Make sure your base price is reasonable (close to current market)
- Don't make spreads too tight - you'll get whipsawed
- Start with small quantities until you're comfortable

## 📞 Support

For issues or questions:
1. Check the log file (`bot.log`) for detailed error information
2. Verify all prerequisites are met
3. Test with small amounts on testnet first

---

**Disclaimer**: This bot is for educational and professional development purposes. Always understand the risks involved in futures trading and never trade with money you cannot afford to lose.