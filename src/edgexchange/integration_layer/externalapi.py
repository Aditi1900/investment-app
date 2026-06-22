import logging
import pandas as pd
from math import inf

import yfinance as yf
from ..common.errors import FetchingError

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# PURPOSE:
#   -ExternalApi provides a external finance fetching abstraction
#   -provides functionality related to fetching live stock data
class ExternalApi:

    # INPUT:
    #   -ticker(str); a stock ticker symbol
    # OUTPUT:
    #   -exist(bool); whether ticker exists in the open market
    # PRECONDITION:
    #   -ticker; matches format [A-Z]{1,5}
    # POSTCONDITION:
    #   -exist; True if ticker exists in open market, False otherwise
    # RAISES:
    #   -FetchingError; if yfinance call fails
    @staticmethod
    def does_ticker_exist(ticker: str) -> bool:

        try: 

            data = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
            exist = not data["Close"].dropna().empty

        except Exception as e:
            raise FetchingError(f"does_ticker_exist failed: {e}") from e

        return exist


    # INPUT:
    #   -ticker(str); a stock ticker symbol
    # OUTPUT:
    #   -max_shares(float); total shares available in open market
    # PRECONDITION:
    #   -ticker; exists in open market
    # POSTCONDITION:
    #   -max_shares; total float shares available in open market for ticker, otherwise inf
    # RAISES:
    #   -FetchingError; if yfinance call fails
    @staticmethod
    def get_float(ticker: str) -> int:

        try:

            raw = yf.Ticker(ticker).fast_info.get('floatShares')

        except Exception as e:
            raise FetchingError(f"get_float failed: {e}") from e

        max_shares = raw if raw is not None else inf

        return max_shares


    # INPUT:
    #   -tickers(list[str]); a list of stock ticker symbols
    # OUTPUT:
    #   -ticker_package(dict[str,float]); live stock prices for all tickers in list
    # PRECONDITION:
    #   -tickers; exist in open market
    # POSTCONDITION:
    #   -ticker_package; holds current market prices for tickers and the ticker symbol related
    # RAISES:
    #   -FetchingError; if yfinance call fails at any point
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:

        ticker_package = {}

        try:

            ticker_dat = None if not tickers else yf.Tickers(" ".join(tickers))

            for t in tickers:

                price = ticker_dat.tickers[t].fast_info.last_price

                if not price:
                    price = yf.Ticker(t).fast_info.last_price

                if not price:
                    raise Exception(t)

                ticker_package[t] = float(price)


        except Exception as e:
            raise FetchingError(f"get_stock_prices failed: {e}") from e

        return ticker_package



    # INPUT:
    #   -tickers(list[str]); stock ticker symbols
    # OUTPUT:
    #   -stock_info(dict[str,dict]); market data snapshot for tickers
    # PRECONDITION:
    #   -tickers; exist in open market with at least 1 day of price history
    # POSTCONDITION:
    #   -stock_info; contains the following keys:
    #       -price(float); current market price
    #       -change(float); percent change from previous close, rounded to 2 decimal places
    #       -positive(bool); True if change >= 0, False otherwise
    #       -sparkline(list[float]); closing prices over last 5 trading days
    #       -open(float); opening price of the most recent trading day
    #       -high(float); intraday high of the most recent trading day
    #       -low(float); intraday low of the most recent trading day
    #       -volume(int); share volume of the most recent trading day
    #       -exchange(str); exchange ticker is listed on
    #       -currency(str); currency prices are denominated in
    #       -fiftyTwoWeekHigh(float); 52-week high price
    #       -fiftyTwoWeekLow(float); 52-week low price
    # RAISES:
    #   -FetchingError; if yfinance call fails or ticker has no price history
    @staticmethod
    def get_stock_info(tickers: list[str]) -> dict[str, dict]:
        
        stock_info = {}

        ticker = None

        def safe_float(val):
            return float(val) if not pd.isna(val) else None
        def safe_int(val):
            return int(val) if not pd.isna(val) else None

        try:
            
            ticker_dat = yf.Tickers(" ".join(tickers))
            hist_all = yf.download(tickers, period="5d", interval="1d", auto_adjust=True, progress=False)
            hist_all.columns = hist_all.columns.swaplevel('Ticker', 'Price')
            hist_all = hist_all.sort_index(axis=1)
            
            for ticker in tickers:
                fi = ticker_dat.tickers[ticker].fast_info
                hist = hist_all[ticker]

                if not hist.empty:
                    price = safe_float(hist["Close"].iloc[-1])
                    close = safe_float(hist["Close"].iloc[-2]) if len(hist) >= 2 else None
                    change = round(((price - close) / close) * 100, 2) if close and price else None
                    positive = change >= 0 if change is not None else None
                    open = safe_float(hist["Open"].iloc[-1])
                    high = safe_float(hist["High"].iloc[-1])
                    low = safe_float(hist["Low"].iloc[-1])
                    volume = safe_int(hist["Volume"].iloc[-1])
                    sparkline = [float(close) for close in hist["Close"].dropna().tolist()]
                else:
                    price = open = high = low = volume = close = sparkline = positive = change = None

                exchange = fi.exchange
                currency = fi.currency
                year_high = fi.year_high
                year_low = fi.year_low

                stock_info[ticker] = {
                    "price": price,
                    "change": change,
                    "positive": positive,
                    "sparkline": sparkline,
                    "open": open,
                    "high": high,
                    "low": low,
                    "volume": volume,
                    "exchange": exchange,
                    "currency": currency,
                    "fiftyTwoWeekHigh": year_high,
                    "fiftyTwoWeekLow": year_low,
                }

        except Exception as e:
            raise FetchingError(f"get_stock_info failed {e}", ticker) from e

        return stock_info


    # INPUT:
    #   -ticker(str); a stock ticker symbol
    # OUTPUT:
    #   -sector(str); market sector the ticker belongs to
    # PRECONDITION:
    #   -ticker; exists in open market
    # POSTCONDITION:
    #   -sector; GICS sector name for ticker (e.g. "Technology"), or "Unknown" if unavailable
    # RAISES:
    #   -FetchingError; if yfinance call fails
    @staticmethod
    def get_sector(ticker: str) -> str:
        try:

            sector = yf.Ticker(ticker).info.get("sector") or "Unknown"
        
        except Exception as e:
            raise FetchingError("Failed to fetch sector") from e

        return sector