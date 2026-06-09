import logging
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

            ticker_dat = None if not tickers else yf.Tickers(" ".join(tickers))

            for t in tickers:

                price = ticker_dat.tickers[t].fast_info.last_price

                if not price:
                    price = yf.Ticker(t).fast_info.last_price

                if not price:
                    raise Exception(t)

                ticker_package[t] = price


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
    def get_stock_info(ticker : str) -> dict:
        try:
            t = yf.Ticker(ticker)
            fi = t.fast_info
            hist = t.history(period="5d", interval="1d")

            if hist.empty:
                raise Exception("Requested Ticker has no history")

            closes = hist["Close"].tolist()
            change = ((fi.last_price - fi.previous_close) / fi.previous_close) * 100

            stock_info = {
                "price": fi.last_price,
                "change": round(change, 2),
                "positive": change >= 0,
                "sparkline": closes,
                "open": hist["Open"].iloc[-1],
                "high": hist["High"].iloc[-1],
                "low": hist["Low"].iloc[-1],
                "volume": int(hist["Volume"].iloc[-1]),
                "exchange": fi.exchange,
                "currency": fi.currency,
                "fiftyTwoWeekHigh": fi.year_high,
                "fiftyTwoWeekLow": fi.year_low,
            }

        except Exception as e:
            raise FetchingError(f"get_stock_info failed: {e}") from e

        return stock_info