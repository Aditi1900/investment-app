import random
from argparse import ArgumentTypeError


_volatile_percent = 0


# INPUT: 
#   -percent(int); an integer representing a percentage of volatility
# OUTPUT:
#   -percent(int); a percentage 1-100
# PRECONDITION:
#   -_volatile_percent; is initialized as a global variable
# POSTCONDITION: 
#   -_volatile_percent; is set to the requested percentage
# RAISES:
#   -ArgumentTypeError; when percent is outside range 1-100
def set_volatile_percent(percent : int):
    global _volatile_percent 

    try:
        percent = int(percent)

        if 0 >= percent or percent > 100:
            raise Exception

        _volatile_percent = percent
    except Exception:
        raise ArgumentTypeError("Volatility must be between 1-100%")

    return percent


# INPUT: 
#   -price(float); a specific stock price
# OUTPUT:
#   -artificial_volatility(float); a random float between +/-(_volatile_percent% of price)
# PRECONDITION: None
# POSTCONDITION: 
#   -artificial volatility; a random float is generated in range of a percentage of the stock
# RAISES: None
def inject_volatility(price : float) -> float:
   
    volatile_range = price/100 * _volatile_percent

    artificial_volatility = random.uniform(-volatile_range, volatile_range)
    
    return artificial_volatility
    