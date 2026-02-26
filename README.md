# upstox-ready-algo

A Python algorithmic trading system built on the [Upstox v2 API](https://upstox.com/developer/api-documentation/).

## Features

- **Authentication** — OAuth2 flow + pre-obtained access-token support
- **Market Data** — live LTP, full quotes, intraday & historical OHLCV candles
- **Order Management** — place market/limit orders, modify, cancel, query order book & trades
- **Portfolio** — holdings, open positions, funds & margin
- **Strategy** — Moving Average Crossover (configurable SMA windows)

## Project structure

```
upstox-ready-algo/
├── algo/
│   ├── __init__.py
│   ├── auth.py          # Upstox OAuth2 authentication
│   ├── config.py        # Configuration from environment variables
│   ├── market_data.py   # Live quotes and OHLCV candles
│   ├── orders.py        # Order placement, modification, cancellation
│   ├── portfolio.py     # Holdings, positions, funds
│   └── strategy.py      # Moving Average Crossover strategy
├── tests/
│   ├── test_market_data.py
│   ├── test_orders.py
│   └── test_strategy.py
├── main.py              # Entry point
├── requirements.txt
└── requirements-dev.txt
```

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Create a `.env` file (or export environment variables):

```dotenv
UPSTOX_API_KEY=<your-api-key>
UPSTOX_API_SECRET=<your-api-secret>
UPSTOX_ACCESS_TOKEN=<your-access-token>   # skip for OAuth2 flow

# Optional trading parameters
UPSTOX_DEFAULT_PRODUCT=I          # I = intraday, D = delivery
STRATEGY_SHORT_WINDOW=5
STRATEGY_LONG_WINDOW=20
INSTRUMENT_KEY=NSE_EQ|INE040A01034  # HDFC Bank
TRADE_QUANTITY=1
CANDLE_INTERVAL=1minute
```

### 3. Run

```bash
python main.py
```

If `UPSTOX_ACCESS_TOKEN` is not set the app will print an authorisation URL,
prompt you for the resulting code, and complete the OAuth2 exchange automatically.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Module reference

### `algo.UpstoxAuth`

Manages OAuth2 authentication.

| Method | Description |
|---|---|
| `get_authorization_url()` | Returns the login URL for the OAuth2 flow |
| `exchange_code(code)` | Exchanges an auth code for an access token |
| `set_access_token(token)` | Directly sets a pre-obtained token |

### `algo.MarketData`

| Method | Description |
|---|---|
| `get_ltp(instrument_keys)` | Last traded price for each instrument |
| `get_full_quote(instrument_keys)` | Full market quote |
| `get_intraday_candles(instrument_key, interval)` | Today's intraday candles |
| `get_historical_candles(...)` | Historical OHLCV candles |
| `get_closing_prices(candles)` | Extract close prices from candle list |

### `algo.OrderManager`

| Method | Description |
|---|---|
| `place_market_order(...)` | Place a market order |
| `place_limit_order(...)` | Place a limit order |
| `modify_order(...)` | Modify an open order |
| `cancel_order(order_id)` | Cancel an open order |
| `get_order_details(order_id)` | Get details of a specific order |
| `get_order_book()` | All orders for the current session |
| `get_trades()` | All executed trades for the current session |

### `algo.Portfolio`

| Method | Description |
|---|---|
| `get_holdings()` | Long-term equity holdings |
| `get_positions()` | Open intraday / short-term positions |
| `get_funds_and_margin(segment)` | Available funds and margin |

### `algo.MovingAverageCrossover`

Simple SMA crossover strategy.

| Method | Description |
|---|---|
| `compute_signal(closing_prices)` | Returns `"BUY"`, `"SELL"`, or `None` |
| `run(interval)` | Fetches candles, computes signal, places order if triggered |

