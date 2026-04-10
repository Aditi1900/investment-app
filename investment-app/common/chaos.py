from enum import Enum

class Chaos(Enum):
    NONE = None
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

def set_entropy(number: int | float, level = Chaos.NONE):

    if level == Chaos.HIGH:
        variation = 2
    elif level == Chaos.MEDIUM:
        variation = 5
    elif level == Chaos.LOW:
        variation = 10
    else:
        entropy = 0,0
        return entropy

    entropy = -number/variation, number/variation

    return entropy