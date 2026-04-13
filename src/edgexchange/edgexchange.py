from argparse import ArgumentParser, Namespace

from .config import App
from .common.entropy import set_volatile_percent


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
    parser.add_argument('-t', "--test", action = "store_true", help = "sets program to testing mode")
    parser.add_argument('-s', "--serve", action = "store_true", help = "program is served on port 0.0.0.0:8000")
    parser.add_argument('-v', "--vol", type = set_volatile_percent, metavar = "%", help = "artificial volatility (percent)")

    args = parser.parse_args()

    return args 


def main():
    args = retrieve_args()

    application = App(testing = args.test, frontend = args.serve)
    application.run()


if __name__ == "__main__" :
    main()