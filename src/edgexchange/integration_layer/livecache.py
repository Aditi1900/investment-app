import time
import threading

from threading import Lock
from collections import defaultdict, Counter

from ..common.errors import FetchingError, LiveCacheError
from ..common.entropy import inject_volatility
from ..common.constants import PRICE_REFRESH_INTERVAL, QUOTE_REFRESH_INTERVAL
from .externalapi import ExternalApi as eapi


cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})
cache_lock = Lock()
ticker_locks = defaultdict(Lock)

watched_tickers = Counter()
watched_lock = Lock()



# INPUT:
#   -tickers(list[str]); list of ticker symbols to fetch and cache
# OUTPUT:
#   -dict[str, float]; mapping of ticker symbols to their fetched prices
# PRECONDITION:
#   -tickers; is non-empty
# POSTCONDITION:
#   -cache; prices and timestamps updated for all tickers in list
# RAISES: None
def update_cache(tickers : list[str]) -> dict[str, float]:
    fresh = eapi.get_stock_prices(tickers)

    with cache_lock:
        for ticker, price in fresh.items():
            cache[ticker]["price"] = price
            cache[ticker]["timestamp"] = time.time()

    return fresh;


# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -cache; watched tickers are refreshed every cycle, quotes evicted >120sec, prices evicted >1sec for unwatched tickers, volatility injected for all fresh prices
# RAISES: None
def run():
    while True:
        # Refresh all watched tickers in one bulk fetch
        with watched_lock:
            new_tickers = list(watched_tickers)

        if new_tickers:
            try:

                update_cache(new_tickers)

            except FetchingError:
                pass


        expired_p = []
        expired_q = []
        now = time.time()
        with cache_lock:
            for ticker, data in cache.items():

                # Stock price eviction/refresh policy
                price = data["price"]
                timestamp = data["timestamp"]

                if timestamp is None or price is None:
                    continue

                if now - timestamp > PRICE_REFRESH_INTERVAL:
                    expired_p.append(ticker)
                else:
                    data["price"] += inject_volatility(price)

                # Stock info quote eviction/refresh policy
                quote = data["quote"]
                quote_timestamp = data["quote_timestamp"]

                if quote is None or quote_timestamp is None:
                    continue

                if now - quote_timestamp > QUOTE_REFRESH_INTERVAL:
                    expired_q.append(ticker)

            # Cache evictions
            for ticker in expired_p:
                cache[ticker]["price"] = None
                cache[ticker]["timestamp"] = None

            for ticker in expired_q:
                cache[ticker]["quote"] = None
                cache[ticker]["quote_timestamp"] = None

        time.sleep(PRICE_REFRESH_INTERVAL)

threading.Thread(target=run, daemon=True).start()


# PURPOSE:
#   -LiveCache provides a cache access abstraction
#   -allows system to store and re-access fresh stocks to reduce api calls
class LiveCache:


    # INPUT:
    #   -tickers(list[str]); list of ticker symbols to watch
    # OUTPUT: None
    # PRECONDITION: None
    # POSTCONDITION:
    #   -watched_tickers; reference count incremented for each ticker in list
    # RAISES: None
    @staticmethod
    def watch(tickers: list[str]) -> None:
        with watched_lock:
            for ticker in tickers:
                watched_tickers[ticker] += 1


    # INPUT:
    #   -tickers(list[str]); list of ticker symbols to unwatch
    # OUTPUT: None
    # PRECONDITION: None
    # POSTCONDITION:
    #   -watched_tickers; reference count decremented for each ticker, removed when count reaches zero
    # RAISES: None
    @staticmethod
    def unwatch(tickers: list[str]) -> None:
        with watched_lock:
            for ticker in tickers:
                watched_tickers[ticker] -= 1
                if watched_tickers[ticker] <= 0:
                    del watched_tickers[ticker]


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_price()
    # RAISES:
    #   -LiveCacheError; propagated from ExternalApi.get_stock_price()
    @staticmethod
    def get_stock_price(ticker: str) -> float:
        try:
            with ticker_locks[ticker]:
                with cache_lock:
                    price = cache[ticker]["price"]

                if price is None:
                    price = eapi.get_stock_price(ticker)

                    with cache_lock:
                        cache[ticker]["price"] = price
                        cache[ticker]["timestamp"] = time.time()

        except FetchingError as e:
            raise LiveCacheError("Failed to find stocks price") from e

        return price


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.does_ticker_exist()
    # RAISES:
    #   -LiveCacheError; propagated from ExternalApi.does_ticker_exist()
    @staticmethod
    def does_ticker_exist(ticker: str) -> bool:
        exist = True

        try:

            if ticker not in cache:
                exist = eapi.does_ticker_exist(ticker)

        except FetchingError as e:
            raise LiveCacheError("Ticker search failed") from e

        return exist


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_float()
    # RAISES:
    #   -LiveCacheError; propagated from ExternalApi.get_float()
    @staticmethod
    def get_float(ticker: str) -> int:
        try:

            if persistent_cache[ticker]["float"] is None:
                persistent_cache[ticker]["float"] = eapi.get_float(ticker)

            max_shares = persistent_cache[ticker]["float"]

        except FetchingError as e:
            raise LiveCacheError("Float shares search failed") from e

        return max_shares


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_sector()
    # RAISES:
    #   -LiveCacheError; propagated from ExternalApi.get_sector()
    @staticmethod
    def get_sector(ticker: str):
        try:

            if persistent_cache[ticker]["sector"] is None:
                persistent_cache[ticker]["sector"] = eapi.get_sector(ticker)

            sector = persistent_cache[ticker]["sector"]

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch stock sector") from e

        return sector


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_info()
    # RAISES:
    #   -LiveCacheError; propagated from ExternalApi.get_stock_info()
    @staticmethod
    def get_stock_info(ticker: str):
        try:

            with ticker_locks[ticker]:
                with cache_lock:
                    stock_info = cache[ticker]["quote"]

                if stock_info is None:
                    stock_info = eapi.get_stock_info(ticker)

                    with cache_lock:     
                        cache[ticker]["quote"] = stock_info
                        cache[ticker]["quote_timestamp"] = time.time()

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch stock info") from e

        return stock_info


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_prices()
    # RAISES:
    #   -LiveCacheError; propagated from ExternalApi.get_stock_prices()
    @staticmethod
    def get_stock_prices(tickers: list[str]) -> dict[str, float]:
        ticker_package = {}

        try:

            with cache_lock:
                cached_tickers = [t for t in tickers if cache[t]["price"] is not None]
                missing_tickers = [t for t in tickers if cache[t]["price"] is None]

                for ticker in cached_tickers:
                    ticker_package[ticker] = cache[ticker]["price"]

            if missing_tickers:
                ticker_package |= update_cache(missing_tickers)

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch requested stock prices") from e

        return ticker_package