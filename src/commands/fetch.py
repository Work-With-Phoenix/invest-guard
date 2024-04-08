# fetch.py

import logging
import yfinance as yf

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_command(args):
    # Function to handle the 'fetch' command
    logger.info("Fetching data...")
    logger.info("Ticker: %s", args.ticker)
    logger.info("Source: %s", args.source)

    if args.source == "yahoo":
        fetch_data_from_yahoo(args.ticker)

def fetch_data_from_yahoo(ticker):
     # Function to fetch data from Yahoo Finance
    # Implement your logic here to fetch data from Yahoo Finance
    try:
        logger.info("Fetching data from Yahoo Finance")
        stock = yf.Ticker(ticker)
        company_name = stock.info.get("longName")
        stock_price = stock.history(period="1d")["Close"].iloc[-1]  # Fetch the closing price from historical data
        logger.info("Company name: %s", company_name)
        logger.info("Stock price: %s", stock_price)
    except Exception as e:
        logger.error("Failed to fetch data from Yahoo Finance: %s", e)
    

def setup_subparser(subparsers):
    # Function to set up argument parsing for the 'fetch' command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch data")
    fetch_parser.add_argument("-t", "--ticker", help="Ticker symbol", required=True)
    fetch_parser.add_argument("-s", "--source", help="Data source", choices=["yahoo", "google"], default="yahoo")

    



 

def execute(args):
    # Function to execute the 'fetch' command based on parsed arguments
    fetch_command(args)
