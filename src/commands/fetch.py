import logging
from datetime import time, datetime, timedelta
import os
import pandas as pd
import pytz
from pytz import UTC
import yfinance as yf
from colorama import Fore, Style
from retry import retry
from urllib3.exceptions import NewConnectionError
import holidays
from tabulate import tabulate
from .helpers.fetch_help import display_help
import numpy as np

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
    "Australia": {"timezone": "Australia/Sydney", "open_time": time(10), "close_time": time(16)},
    "Hong Kong": {"timezone": "Asia/Hong_Kong", "open_time": time(9, 30), "close_time": time(16)},
    "India": {"timezone": "Asia/Kolkata", "open_time": time(9, 15), "close_time": time(15, 30)},
    "Canada": {"timezone": "America/Toronto", "open_time": time(9, 30), "close_time": time(16)},
    "Nigeria": {"timezone": "Africa/Lagos", "open_time": time(10), "close_time": time(16)},
    "South Africa": {"timezone": "Africa/Johannesburg", "open_time": time(9, 30), "close_time": time(17)},
    "Kenya": {"timezone": "Africa/Nairobi", "open_time": time(9, 30), "close_time": time(15)},
    "Ghana": {"timezone": "Africa/Accra", "open_time": time(10), "close_time": time(16)},
    "Egypt": {"timezone": "Africa/Cairo", "open_time": time(10), "close_time": time(15)},
    "Morocco": {"timezone": "Africa/Casablanca", "open_time": time(9, 30), "close_time": time(16, 30)},
    # Add more African markets as needed
}

def is_market_open(default_timezone="US/Eastern", provided_timezone=None):
    try:
        market_info = MARKET_TIMES.get(provided_timezone, MARKET_TIMES.get(default_timezone))
        if not market_info:
            raise ValueError(f"Market timezone '{provided_timezone}' not found.")
        
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
    except Exception as e:
        raise ValueError(f"Market timezone '{provided_timezone}' not found: {e}")

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



def fetch_data(asset_type, ticker, start_date=None, end_date=None, market_open=None):
    data = {}
    try:
        stock = yf.Ticker(ticker)
        
        if start_date and end_date:
            # Fetch historical data based on dates
            history = stock.history(start=start_date, end=end_date)
            if not history.empty:
                history['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history['Market Cap'] = history.apply(lambda row: calculate_market_cap(row['Close'], row['Volume']), axis=1)
                
                data = history.reset_index().to_dict(orient='records')
            else:
                raise ValueError("No historical data available for the specified date range.")
        else:
            # Fetch live data or historical data when the market is open
            if market_open or asset_type in ["crypto", "currency"]:
                live_data = stock.history(period="1d")
                if not live_data.empty:
                    live_data['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    live_data['Market Cap'] = live_data.apply(lambda row: calculate_market_cap(row['Close'], row['Volume']), axis=1)
                    data = live_data.reset_index().to_dict(orient='records')
                else:
                    raise ValueError("No live data available.")
            else:
                # Fetch historical data for traditional market-dependent assets when the market is closed
                history = stock.history(period="2d")
                if len(history) >= 2:
                     history['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                     history['Market Cap'] = history.apply(lambda row: calculate_market_cap(row['Close'], row['Volume']), axis=1)
                     data = history.reset_index().to_dict(orient='records')
                else:
                    raise ValueError("No historical data available when the market was closed.")
                

            

    except Exception as e:
        raise RuntimeError(f"Failed to fetch data for {ticker}: {e}")
        
    return data
def export_data(data, ticker, start_date, end_date, export_format, export_filename):
    # Extract the file extension from the provided filename
    filename, extension = os.path.splitext(export_filename)

    # Construct dynamic filename
    dynamic_filename = f"{ticker}_data_{start_date}_to_{end_date}.{export_format}"

    # Construct export file path
    export_dir = os.path.join(os.path.expanduser("~"), "Documents", "invest_guard")
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, export_filename if extension else dynamic_filename)

    # Convert 'Timestamp' column to datetime type if it's not already in datetime format
    if isinstance(data, pd.DataFrame) and 'Timestamp' in data.columns:
        data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')

    if export_format == "xlsx":
        # Export to Excel with pandas ExcelWriter
        if isinstance(data, pd.DataFrame):
            # Convert datetime to string format without timezone information
            for col in data.columns:
                if pd.api.types.is_datetime64_any_dtype(data[col]):
                    data[col] = data[col].dt.strftime('%Y-%m-%d %H:%M:%S')

            with pd.ExcelWriter(filepath) as writer:
                data.to_excel(writer, index=False)
        else:
            raise ValueError("Data must be a DataFrame when exporting to Excel.")
    else:
        # For other export formats (e.g., csv, json)
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        elif not isinstance(data, list):
            raise ValueError("Data must be either a DataFrame or a list of dictionaries.")

        # Export data to specified format
        if export_format == "csv":
            pd.DataFrame(data).to_csv(filepath, index=False)
        elif export_format == "json":
            pd.DataFrame(data).to_json(filepath, orient="records")
        else:
            raise ValueError(f"Invalid export format: {export_format}")

        print(f"Data exported successfully to {filepath}.")

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
            if args.start_date and args.end_date:
                logger.info("Fetching historical data...")
                data = fetch_data(args.asset_type, args.ticker, args.start_date, args.end_date)
            else:
                default_timezone = args.timezone if args.timezone else "United States"
                market_open, closure_info = is_market_open(default_timezone, args.timezone)
                if args.asset_type == "crypto" or market_open or args.asset_type == "currency":
                    logger.info("Market open: True")
                else:
                    logger.info("Market open: False")
                    if not market_open:
                        logger.info("Closure info: %s", closure_info)
                if market_open or args.asset_type in ["currency", "crypto"]:
                    logger.info("Fetching live data...")
                    data = fetch_data(args.asset_type, args.ticker)
                else:
                    logger.info("Fetching historical data...")
                    data = fetch_data(args.asset_type, args.ticker)
        else:  # For crypto and other assets
            logger.info("Fetching live data...")
            data = fetch_data(args.asset_type, args.ticker)

        if data:
            headers = [LABELS.get(key, key) for key in data[0].keys()]  # Get headers from the first data entry
            rows = [[value for value in entry.values()] for entry in data]  # Extract values from each entry
            table = tabulate(rows, headers=headers, tablefmt="grid")
            print(table)

            # Check if export format is provided
            if args.export_format:
                # convert data to DataFrame it it's alist
                if isinstance(data, list):
                    data = pd.DataFrame(data)

                # Export data if export option is provided
                export_data(data, args.ticker, args.start_date, args.end_date, args.export_format, args.export_filename)
        else:
            logger.warning("No data fetched for %s", args.ticker)

    else:
        logger.warning("Invalid source specified. Only 'yahoo' source is supported.")

def setup_subparser(subparsers):
    fetch_parser = subparsers.add_parser("fetch", help="Fetch data")
    fetch_parser.add_argument("-t", "--ticker", help="Ticker symbol", required=True)
    fetch_parser.add_argument("-s", "--source", help="Data source", choices=["yahoo", "google"], default="yahoo")
    fetch_parser.add_argument("-z", "--timezone", help="Timezone")
    fetch_parser.add_argument("--asset-type", help="Asset type to fetch data for", choices=["stock", "etf", "crypto", "currency", "commodity"], required=True)
    fetch_parser.add_argument("--start-date", help="Start date for historical data (YYYY-MM-DD)")
    fetch_parser.add_argument("--end-date", help="End date for historical data (YYYY-MM-DD)")
    fetch_parser.add_argument("--export-format", help="Export format for f`etched data", choices=["csv", "json", "xlsx"])
    fetch_parser.add_argument("--export-filename", help="Export filename for fetched data")


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
def setup_subparser(subparsers):
    fetch_parser = subparsers.add_parser("fetch", help="Fetch data")
    fetch_parser.add_argument("-t", "--ticker", help="Ticker symbol", required=True)
    fetch_parser.add_argument("-s", "--source", help="Data source", choices=["yahoo"], default="yahoo")
    fetch_parser.add_argument("-z", "--timezone", help="Timezone")
    fetch_parser.add_argument("--asset-type", help="Asset type to fetch data for", choices=["stock", "etf", "crypto", "currency", "commodity"], required=True)
    fetch_parser.add_argument("--start-date", help="Start date for historical data fetch")
    fetch_parser.add_argument("--end-date", help="End date for historical data fetch")
    fetch_parser.add_argument("--export-format", help="Export format for fetched data", choices=["csv", "json", "xlsx"])
    fetch_parser.add_argument("--export-filename", help="Export filename for fetched data")

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
        display_help()

    if args.command == "fetch":
        execute(args)
    else:
        print("Invalid command. Please use 'fetch' command.")
