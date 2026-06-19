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
    #   -price(float); live stock price
    # PRECONDITION:
    #   -ticker; exists in open market
    # POSTCONDITION:
    #   -price; current market price for ticker
    # RAISES:
    #   -FetchingError; if yfinance call fails
    @staticmethod
    def get_stock_price(ticker: str) -> float:

        try:

            price = yf.Ticker(ticker).fast_info.last_price

        except Exception as e:
            raise FetchingError(f"get_stock_price failed: {e}") from e

        return price


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

            exist = yf.Ticker(ticker).fast_info.last_price is not None

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
            if not tickers:
                return ticker_package

            data = yf.download(tickers, period="1d", interval="1m", auto_adjust=True, progress=False)

            for t in tickers:
                series = data["Close"][t].dropna() if len(tickers) > 1 else data["Close"].dropna()

                if series.empty:
                    series = yf.download(t, period="1d", interval="1m", auto_adjust=True, progress=False)["Close"].dropna()
                    
                if series.empty:
                    raise Exception(t)

                ticker_package[t] = float(series.iloc[-1])

        except Exception as e:
            raise FetchingError(f"get_stock_prices failed: {e}") from e

        return ticker_package



    # INPUT:
    #   -ticker(str); a stock ticker symbol
    # OUTPUT:
    #   -stock_info(dict); market data snapshot for ticker
    # PRECONDITION:
    #   -ticker; exists in open market with at least 1 day of price history
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
        current_ticker = None
        try:
            stock_info = {}

            ticker_dat = None if not tickers else yf.Tickers(" ".join(tickers))
            hist_all = yf.download(tickers, period="5d", interval="1d", auto_adjust=True, progress=False)
            hist_all.columns = hist_all.columns.swaplevel('Ticker', 'Price')
            hist_all = hist_all.sort_index(axis=1)

            for t in tickers:
                current_ticker = t
                fi = ticker_dat.tickers[t].fast_info
                hist = hist_all[t]

                closes = hist["Close"].dropna().tolist()
                last_price = hist["Close"].iloc[-1] if not hist.empty else None
                previous_close = hist["Close"].iloc[-2] if len(hist) >= 2 else None

                if last_price and previous_close:
                    change = ((last_price - previous_close) / previous_close) * 100
                else:
                    change = None

                exchange = fi.exchange
                currency = fi.currency
                year_high = fi.year_high
                year_low = fi.year_low

                stock_info[t] = {
                    "price": float(last_price) if last_price is not None else None,
                    "change": round(change, 2) if change is not None else None,
                    "positive": bool(change >= 0) if change is not None else None,
                    "sparkline": [float(c) for c in closes] if closes else None,
                    "open": float(hist["Open"].iloc[-1]) if not hist.empty else None,
                    "high": float(hist["High"].iloc[-1]) if not hist.empty else None,
                    "low": float(hist["Low"].iloc[-1]) if not hist.empty else None,
                    "volume": int(hist["Volume"].iloc[-1]) if not hist.empty and not pd.isna(hist["Volume"].iloc[-1]) else None,
                    "exchange": exchange,
                    "currency": currency,
                    "fiftyTwoWeekHigh": float(year_high) if year_high is not None else None,
                    "fiftyTwoWeekLow": float(year_low) if year_low is not None else None,
                }

        except Exception as e:
            raise FetchingError(f"get_stock_info failed {e}", ticker=current_ticker) from e

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