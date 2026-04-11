from argparse import ArgumentTypeError

import random

_volatile_percent = 0


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


def inject_volatility(price : float):
   
    volatile_range = price/100 * _volatile_percent

    artificial_volatility = random.uniform(-volatile_range, volatile_range)
    
    return artificial_volatility
    