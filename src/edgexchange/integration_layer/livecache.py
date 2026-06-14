import time
import threading
import math

from threading import Lock
from collections import defaultdict

from ..common.errors import FetchingError, LiveCacheError
from ..common import constants
from ..common.entropy import inject_volatility
from .externalapi import ExternalApi as eapi


cache = defaultdict(lambda : {"price" : None, "timestamp" : None, "quote" : None, "quote_timestamp" : None})
persistent_cache = defaultdict(lambda : {"sector" : None, "float" : None})
cache_lock = Lock()

fetch_locks = {
    "bulk" : Lock(),
    "price":  Lock(),
    "quote":  Lock(),
    "float":  Lock(),
    "sector": Lock(),
    "exists": Lock(),
}

sp500 = [
    "NVDA", "GOOGL", "GOOG", "AAPL", "MSFT", "AMZN", "AVGO", "META", "TSLA", "BRK.B",
    "LLY", "JPM", "V", "UNH", "XOM", "MA", "COST", "HD", "PG", "WMT",
    "NFLX", "JNJ", "CRM", "BAC", "ABBV", "ORCL", "CVX", "MRK", "WFC", "CSCO",
    "NOW", "ACN", "IBM", "GS", "LIN", "PM", "T", "TMO", "MCD", "ABT",
    "INTU", "AXP", "CAT", "ISRG", "VZ", "AMGN", "SPGI", "PFE", "DHR", "TXN",
    "NEE", "RTX", "UBER", "BKNG", "HON", "LOW", "MS", "UNP", "BLK", "AMAT",
    "BSX", "C", "SYK", "PLD", "DE", "VRTX", "ETN", "ADI", "SBUX", "GILD",
    "ADP", "MMC", "PANW", "LRCX", "MDT", "BMY", "CB", "SCHW", "AMT", "TMUS",
    "MU", "SO", "BA", "MDLZ", "KLAC", "CI", "PGR", "REGN", "DUK", "ZTS",
    "MCO", "COP", "CME", "TJX", "WELL", "GE", "SNPS", "CDNS", "AON", "ICE",
    "WM", "CEG", "FCX", "CSX", "EOG", "ITW", "ELV", "PSA", "NOC", "SHW",
    "PH", "HCA", "USB", "GEV", "EMR", "AJG", "OKE", "TT", "CTAS", "NKE",
    "ORLY", "APH", "PCAR", "FDX", "MMM", "MSI", "AFL", "COF", "ECL", "ROP",
    "ADSK", "AIG", "MPC", "PSX", "APD", "TDG", "SLB", "TRV", "BDX", "FICO",
    "NSC", "NEM", "MSCI", "KMB", "MET", "NXPI", "EW", "AZO", "O", "RSG",
    "PCG", "D", "CARR", "SRE", "PAYX", "STZ", "FAST", "HLT", "CTVA", "ALL",
    "GM", "F", "ROST", "MCHP", "GEHC", "GWW", "IDXX", "KDP", "PPG", "PRU",
    "A", "ODFL", "LHX", "HUM", "VRSK", "OTIS", "AME", "CMG", "CPRT", "EXC",
    "DHI", "IR", "FANG", "KVUE", "CTSH", "MNST", "CCI", "DXCM", "ACGL", "KR",
    "DVN", "PWR", "XEL", "ROK", "EA", "WAB", "BIIB", "HWM", "HAL", "URI",
    "FITB", "MTB", "KHC", "EFX", "ANSS", "PEG", "GLW", "EBAY", "WBD", "DECK",
    "DD", "CHD", "BF.B", "KEYS", "ZBH", "RMD", "DAL", "WTW", "TTWO", "LEN",
    "WEC", "VLTO", "LVS", "ETR", "EIX", "DOV", "CAH", "INVH", "CBRE", "ON",
    "AXON", "NVR", "PHM", "HUBB", "RF", "HBAN", "IFF", "SBAC", "AVB", "TRGP",
    "BR", "HPQ", "MOH", "LYB", "STE", "CINF", "WAT", "BALL", "ULTA", "TYL",
    "OMC", "MKC", "EXPD", "NTAP", "STT", "AEP", "PPL", "GIS", "FTV", "DTE",
    "IRM", "AWK", "ES", "CBOE", "GRMN", "AEE", "VICI", "ARE", "TDY", "HOLX",
    "DOC", "NUE", "PODD", "BAX", "CMS", "HSY", "STLD", "CF", "CLX", "TSN",
    "LH", "EQR", "EXAS", "APTV", "COO", "JBHT", "EVRG", "LUV", "PKG", "SNA",
    "SWK", "NTRS", "EXPD", "BRO", "ERIE", "ZBRA", "ALGN", "POOL", "TECH", "MAS",
    "DRI", "TER", "CHRW", "AIZ", "WDC", "JKHY", "CPT", "SWKS", "HRL", "FMC",
    "AKAM", "DGX", "IPG", "HSIC", "TAP", "NDSN", "CTLT", "PNR", "MKTX", "UDR",
    "L", "QRVO", "BBWI", "EPAM", "VTRS", "HII", "LNC", "DVA", "MHK", "XRAY",
    "CPB", "AOS", "IVZ", "RL", "GNRC", "ALLE", "LUMN", "BWA", "PVH", "SEE",
    "HAS", "CE", "WBA", "CZR", "BEN", "NCLH", "ALK", "CCL", "RCL", "MGM",
    "WYNN", "TPR", "VFC", "FOX", "FOXA", "NWS", "NWSA", "FRT", "REG", "SPG",
    "MAC", "KIM", "HST", "EQT", "MRO", "APA", "OXY", "PXD", "VLO", "HES",
    "CVS", "CI", "HIG", "PFG", "TROW", "BK", "NTRS", "FIS", "FISV", "GPN",
    "MA", "V", "DFS", "SYF", "ALLY", "CFG", "ZION", "CMA", "KEY", "PBCT",
    "IEX", "RJF", "SEIC", "NDAQ", "CBSH", "FHN", "SNV", "CINF", "TMK", "GL"
    ]




# INPUT: None
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -cache; all tickers prices un-updated >1sec are removed (quotes removed >120sec), simulated volatility is injected here if any
# RAISES: None
def run():
    while True:
        expired_p = []
        expired_q = []
        now = time.time()
        with cache_lock:
            for ticker, data in cache.items():
                
                #Stock price eviction/refresh policy
                price = data["price"]
                timestamp = data["timestamp"]

                if timestamp is None or price is None:
                    continue

                if now - timestamp > constants.PRICE_REFRESH_INTERVAL: 
                    expired_p.append(ticker)
                else:  
                   data["price"] += inject_volatility(price)

                
                #Stock info quote eviciton/refresh policy
                quote = data["quote"]
                quote_timestamp = data["quote_timestamp"]

                if quote is None or quote_timestamp is None:
                    continue

                if now - quote_timestamp > constants.QUOTE_REFRESH_INTERVAL:
                    expired_q.append(ticker)

            #Cache evictions
            for ticker in expired_p:
                cache[ticker]["price"] = None
                cache[ticker]["timestamp"] = None

            for ticker in expired_q:
                cache[ticker]["quote"] = None
                cache[ticker]["quote_timestamp"] = None

        elapsed = time.time() - now
        time.sleep(max(0, constants.PRICE_REFRESH_INTERVAL - elapsed))



def warm_cache():
    try:
        with cache_lock:
            unwarm = [t for t in sp500 if cache[t]["price"] is None]

        if unwarm:
            warm = eapi.get_stock_prices(unwarm)
        else:
            warm = eapi.get_stock_prices(sp500)

        with cache_lock:
            for ticker, price in warm.items():
                cache[ticker]["price"] = price + inject_volatility(price)
                cache[ticker]["timestamp"] = time.time()

    except FetchingError:
        pass


def cache_warmer():
    while True:
        start = time.time()
        warm_cache()
        elapsed = time.time() - start

        warmtime = constants.PRICE_REFRESH_INTERVAL / 2
        time.sleep(max(0, warmtime - elapsed))

threading.Thread(target = cache_warmer, daemon = True).start()
threading.Thread(target = run, daemon = True).start()



# PURPOSE:
#   -LiveCache provides a cache access abstraction
#   -allows system to store and re-access fresh stocks to reduce api calls 
class LiveCache:

    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_stock_price()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_stock_price()
    @staticmethod
    def get_stock_price(ticker : str) -> float:
        try:

            with fetch_locks["price"]:
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
    def does_ticker_exist(ticker : str) -> bool:
        exist = True

        try:

            with fetch_locks["exists"]:
                if ticker not in cache:
                    exist = eapi.does_ticker_exist(ticker)

        except FetchingError as e:
            raise LiveCacheError("Ticker search failed") from e

        return exist


    # INPUT/OUTPUT/PRECONDITION/POSTCONDITION: see respective fields in ExternalApi.get_float()
    # RAISES: 
    #   -LiveCacheError; propagated from ExternalApi.get_float()
    @staticmethod
    def get_float(ticker : str) -> int:
        try:

            with fetch_locks["float"]:
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
    def get_sector(ticker : str):
        try:

            with fetch_locks["sector"]:
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

            with fetch_locks["quote"]:
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

            with fetch_locks["bulk"]:
                with cache_lock:
                    cached_tickers = [t for t in tickers if cache[t]["price"] is not None]
                    missing_tickers = [t for t in tickers if cache[t]["price"] is None]
                    
                    for ticker in cached_tickers:
                        ticker_package[ticker] = cache[ticker]["price"]

                
                fresh = eapi.get_stock_prices(missing_tickers)

                with cache_lock:
                    for ticker, price in fresh.items():
                        cache[ticker]["price"] = price
                        cache[ticker]["timestamp"] = time.time()

            
                    ticker_package |= fresh

        except FetchingError as e:
            raise LiveCacheError("Failed to fetch requested stock prices") from e

        return ticker_package