import logging
from datetime import time, datetime, timedelta
import pytz
import yfinance as yf
from colorama import Fore, Style
from retry import retry
from urllib3.exceptions import NewConnectionError
import holidays
from tabulate import tabulate

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define labels for data
LABELS = {
    "company_name": "Company Name",
    "stock_price": "Stock Price",
    "open_price": "Open Price",
    "high_price": "High Price",
    "low_price": "Low Price",
    "prev_close_price": "Previous Close Price",
    "volume": "Volume",
    "market_cap": "Market Capitalization",
    "exchange": "Stock Exchange",
    "bid": "Bid",
    "ask": "Ask",
    "day_range": "Day's Range",
    "52_week_range": "52 Week Range",
    "beta": "Beta (5Y Monthly)",
    "pe_ratio": "PE Ratio (TTM)",
    "eps": "EPS (TTM)",
    "earnings_date": "Earnings Date",
    "forward_dividend_yield": "Forward Dividend & Yield",
    "ex_dividend_date": "Ex-Dividend Date",
    "1y_target_est": "1y Target Est",
    "current_price": "Current Price" 
}

# Color codes
COLOR_GREEN = Fore.GREEN
COLOR_YELLOW = Fore.YELLOW
COLOR_RED = Fore.RED
COLOR_BLUE = Fore.BLUE
COLOR_RESET = Style.RESET_ALL

# Market timezones and open/close times
MARKET_TIMES = {
    "United States": {"timezone": "US/Eastern", "open_time": time(9, 30), "close_time": time(16)},
    "Europe": {"timezone": "Europe/Berlin", "open_time": time(9), "close_time": time(17, 30)},
    "Asia": {"timezone": "Asia/Tokyo", "open_time": time(9), "close_time": time(15)},
}

def is_market_open(exchange):
    try:
        market_info = MARKET_TIMES[exchange]
    except KeyError:
        return False, COLOR_RED + f"Market '{exchange}' not found." + COLOR_RESET

    timezone = pytz.timezone(market_info["timezone"])
    now = datetime.now(timezone)
    open_time = timezone.localize(datetime.combine(now.date(), market_info["open_time"]))
    close_time = timezone.localize(datetime.combine(now.date(), market_info["close_time"]))

    if now.weekday() >= 5 or now.strftime('%Y-%m-%d') in holidays.CountryHoliday("US"):
        return False, COLOR_RED + "Reason: Today is a holiday or weekend." + COLOR_RESET
    elif open_time <= now <= close_time:
        return True, ""
    else:
        # Calculate the next open time
        next_open_date = now.date() + timedelta(days=1)
        next_open_time = timezone.localize(datetime.combine(next_open_date, market_info["open_time"]))
        closure_reason = COLOR_RED + "Reason: Market is closed outside of trading hours." + COLOR_RESET
        next_open_message = COLOR_YELLOW + f"Next market open: {next_open_time.strftime('%Y-%m-%d %H:%M')} ({market_info['timezone']})" + COLOR_RESET
        return False, closure_reason + "\n" + next_open_message


@retry((ConnectionError, NewConnectionError), delay=5, backoff=2, tries=3)
def calculate_market_cap(current_price, volume):
    """
    Calculate market capitalization.
    Market Cap = Current Price * Volume
    """
    try:
        current_price = float(current_price)
        volume = float(volume)
        return current_price * volume
    except ValueError:
        # Handle the case where either current_price or volume cannot be converted to float
        return None  # Or any appropriate error handling logic

def fetch_data(asset_type, ticker, market_open=None):
    data = {}
    try:
        stock = yf.Ticker(ticker)
        
        if asset_type in ["crypto", "currency"]:
            # Fetch live data for cryptocurrencies and certain currencies
            # logger.info("Fetching live data...")
            live_data = stock.history(period="1d")
            logger.debug("Live data: %s", live_data)
            if not live_data.empty:
                data["Open Price"] = COLOR_GREEN + str(live_data["Open"].iloc[-1]) + COLOR_RESET
                data["High Price"] = COLOR_GREEN + str(live_data["High"].iloc[-1]) + COLOR_RESET
                data["Low Price"] = COLOR_GREEN + str(live_data["Low"].iloc[-1]) + COLOR_RESET
                data["Close Price"] = COLOR_GREEN + str(live_data["Close"].iloc[-1]) + COLOR_RESET
                data["Volume"] = COLOR_GREEN + str(live_data["Volume"].iloc[-1]) + COLOR_RESET
                data["Current Price"] = COLOR_GREEN + str(live_data["Close"].iloc[-1]) + COLOR_RESET  # Add current price
                data["Market Cap"] = calculate_market_cap(data["Current Price"], data["Volume"])
            else:
                logger.warning("No live data available.")
                
        elif market_open:
            # Fetch live data for traditional market-dependent assets when the market is open
            # logger.info("Fetching live data...")
            live_data = stock.history(period="1d")
            logger.debug("Live data: %s", live_data)
            if not live_data.empty:
                data["Open Price"] = COLOR_GREEN + str(live_data["Open"].iloc[-1]) + COLOR_RESET
                data["High Price"] = COLOR_GREEN + str(live_data["High"].iloc[-1]) + COLOR_RESET
                data["Low Price"] = COLOR_GREEN + str(live_data["Low"].iloc[-1]) + COLOR_RESET
                data["Close Price"] = COLOR_GREEN + str(live_data["Close"].iloc[-1]) + COLOR_RESET
                data["Current Price"] = COLOR_GREEN + str(live_data["Close"].iloc[-1]) + COLOR_RESET  # Add current price
                data["Volume"] = COLOR_GREEN + str(live_data["Volume"].iloc[-1]) + COLOR_RESET
                 # Calculate market cap
                current_price = live_data["Close"].iloc[-1]
                volume = live_data["Volume"].iloc[-1]
                market_cap = calculate_market_cap(current_price, volume)
                data["Market Cap"] = market_cap
            else:
                logger.warning("No live data available.")
                
        else:
            # Fetch historical data for traditional market-dependent assets when the market is closed
            # logger.info("Fetching historical data...")
            history = stock.history(period="2d")
            logger.debug("Historical data: %s", history)
            if len(history) >= 2:
                data["Previous Close Price"] = COLOR_GREEN + str(history["Close"].iloc[-2]) + COLOR_RESET
                # Calculate market cap based on the previous close price and volume of the last trading day
                previous_close_price = history["Close"].iloc[-2]
                volume = history["Volume"].iloc[-1]
                market_cap = calculate_market_cap(previous_close_price, volume)
                data["Market Cap"] = market_cap   

        # Fetch company name and market capitalization
        info = stock.info
        for key, label in LABELS.items():
            if key in info:
                value = info[key]
                data[label] = COLOR_GREEN + str(value) + COLOR_RESET if value is not None else COLOR_BLUE + "Unavailable" + COLOR_RESET
        company_name = info.get("longName", None)
        data[LABELS["company_name"]] = COLOR_GREEN + str(company_name) + COLOR_RESET if company_name is not None else COLOR_BLUE + "Unavailable" + COLOR_RESET
        data["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        logger.error(COLOR_RED + "Failed to fetch data: %s" % e + COLOR_RESET)
        
    return data

def fetch_command(args):
    logger.info("Fetching data...")
    logger.info("Args: %s", args)  # Log the args object to verify its contents
    logger.info("Ticker: %s", args.ticker if hasattr(args, 'ticker') else None)  # Access args.ticker attribute if it exists
    logger.info("Source: %s", args.source)
    logger.info("Asset type: %s", args.asset_type)

    logger.info(COLOR_YELLOW + "Checking internet connection..." + COLOR_RESET)
    connected = True  # Simulate internet check, change to actual check

    if not connected:
        logger.warning(COLOR_YELLOW + "No internet connection. Retrying in 5 seconds..." + COLOR_RESET)
        time.sleep(5)
        connected = False

    logger.info(COLOR_GREEN + "Connection established." + COLOR_RESET)

    if args.source == "yahoo":
        if args.asset_type in ["stock", "etf", "currency", "commodity"]:
            if args.timezone:
                market_open, closure_info = is_market_open(args.timezone)
                if args.asset_type == "crypto" or market_open or args.asset_type == "currency":
                    logger.info("Market open: True")
                else:
                    logger.info("Market open: False")
                    if not market_open:
                        logger.info("Closure info: %s", closure_info)
                if market_open or args.asset_type in ["currency", "crypto"]:
                    logger.info("Fetching live data...")
                    stock = yf.Ticker(args.ticker)
                    data = fetch_data(args.asset_type, args.ticker, market_open)
                else:
                    logger.info("Fetching historical data...")
                    stock = yf.Ticker(args.ticker)
                    data = fetch_data(args.asset_type, args.ticker, market_open)
            else:
                default_timezone = "United States"
                market_open, closure_info = is_market_open(default_timezone)
                if args.asset_type == "crypto" or market_open or args.asset_type == "currency":
                    logger.info("Market open: True")
                else:
                    logger.info("Market open: False")
                    if not market_open:
                        logger.info("Closure info: %s", closure_info)
                if market_open or args.asset_type in ["currency", "crypto"]:
                    logger.info("Fetching live data...")
                    stock = yf.Ticker(args.ticker)
                    data = fetch_data(args.asset_type, args.ticker, market_open)
                else:
                    logger.info("Fetching historical data...")
                    stock = yf.Ticker(args.ticker)
                    data = fetch_data(args.asset_type, args.ticker, market_open)
        else:  # For crypto and other assets
            logger.info("Fetching live data...")
            stock = yf.Ticker(args.ticker)
            data = fetch_data(args.asset_type, args.ticker, market_open=True)  # Fetch live data without checking market status

        if data:
            headers = [LABELS.get(key, key) for key in data.keys()]
            rows = [[value for value in data.values()]]
            table = tabulate(rows, headers=headers, tablefmt="grid")
            print(table)
        else:
            logger.warning("No data fetched for %s", args.ticker)

def setup_subparser(subparsers):
    fetch_parser = subparsers.add_parser("fetch", help="Fetch data")
    fetch_parser.add_argument("-t", "--ticker", help="Ticker symbol", required=True)
    fetch_parser.add_argument("-s", "--source", help="Data source", choices=["yahoo", "google"], default="yahoo")
    fetch_parser.add_argument("-z", "--timezone", help="Timezone")
    fetch_parser.add_argument("--asset-type", help="Asset type to fetch data for", choices=["stock", "etf", "crypto", "currency", "commodity"], required=True)

def execute(args):
    if args.command == "fetch":
        fetch_command(args)
    else:
        print("Invalid command. Please use 'fetch' command.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Investment Guard CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    setup_subparser(subparsers)

    args = parser.parse_args()

    if args.command == "fetch":
        execute(args)
    else:
        print("Invalid command. Please use 'fetch' command.")
