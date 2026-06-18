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
    def get_stock_info(tickers : list[str]) -> dict[str, dict]:
        try:
            stock_info = {}

            ticker_dat = None if not tickers else yf.Tickers(" ".join(tickers))
            hist_all = yf.download(tickers, period="5d", interval="1d", auto_adjust=True, progress=False)
            hist_all.columns = hist_all.columns.swaplevel('Ticker', 'Price')
            hist_all = hist_all.sort_index(axis=1)

            for t in tickers:
                fi = ticker_dat.tickers[t].fast_info
            
                hist = hist_all[t]

                closes = hist["Close"].tolist()

                previous_close = fi.previous_close

                if previous_close:
                    change = ((fi.last_price - previous_close) / previous_close) * 100
                else:
                    change = 0

                stock_info[t] = {
                "price": fi.last_price,
                "change": round(change, 2) if previous_close else None,
                "positive": (change >= 0) if previous_close else None,
                "sparkline": closes if not hist.empty else None,
                "open": hist["Open"].iloc[-1] if not hist.empty else None,
                "high": hist["High"].iloc[-1] if not hist.empty else None,
                "low": hist["Low"].iloc[-1] if not hist.empty else None,
                "volume": int(hist["Volume"].iloc[-1]) if not hist.empty else None,
                "exchange": fi.exchange,
                "currency": fi.currency,
                "fiftyTwoWeekHigh": fi.year_high,
                "fiftyTwoWeekLow": fi.year_low,
                }   

        except Exception as e:
            raise FetchingError(f"get_stock_info failed {e}") from e

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