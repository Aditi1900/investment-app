from .config import App
from .common.entropy import set_volatile_percent
from argparse import ArgumentParser, Namespace

# INPUT: None
# OUTPUT:
#   -args(Namespace); entered system arguments, -t testing mode flag, -s frontend server flag
# PRECONDITION: None
# POSTCONDITION:
#   -args; system arguments have been parsed from terminal
# RAISES:
#   -SystemExit; on invalid argument insertion
def retrieve_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-t', action = "store_true", help = "sets program to testing mode")
    parser.add_argument('-s', action = "store_true", help = "program is served on port 0.0.0.0:8000")
    parser.add_argument('-v', type = set_volatile_percent, help = "artificial volatility (percent)")

    args = parser.parse_args()

    return args 


def main():
    args = retrieve_args()

    investment_app = App(testing = args.t, frontend = args.s)
    investment_app.run()


if __name__ == "__main__" :
    main()