from matplotlib.backend_bases import CloseEvent
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tabulate import tabulate
import pandas as pd


# PURPOSE:
#   -Visualizer provides a data visualization abstraction
#   -provides an isolated layer that allows for construction of data charts
class Visualizer:
    def __init__(self):
        self.fig = None
        self.ax = None
        self.ani = None

    # INPUT:
    #   -package_portfolio_data(callable); portfolio data formatter returns list[dict[str|int]]
    # OUTPUT: None
    # PRECONDITION:
    #   -package_portfolio_data; returns list, each dict contains 'ticker'(str), 'value'(float), 'label'(str) and the last item is portfolio total(float)
    # POSTCONDITION:
    #   -self.fig, self.ax, self.ani; constructed and active if no chart exists and data is non-empty, otherwise unchanged
    #   -execution; chart display does not block program
    # RAISES: None
    def display_pie_chart(self, package_portfolio_data : callable) -> None:
        if self.fig is None and package_portfolio_data()["holdings"]:
            self.fig, self.ax = plt.subplots()
            self.fig.canvas.mpl_connect('close_event', self.clean_up)

            def update(frame):
                portfolio_data = package_portfolio_data()

                self.ax.clear()

                if not portfolio_data["holdings"]:
                    return

                df = pd.DataFrame(portfolio_data["holdings"])
                self.ax.pie(df['value'], labels=df['label'], autopct='%1.0f%%')
                self.ax.set_title(f"Portfolio Distribution")
                self.ax.set_xlabel(f"Total portfolio value: {portfolio_data['total']}")

            self.ani = animation.FuncAnimation(self.fig, update, interval=1000, cache_frame_data=False)
            plt.show(block=False)    


    # INPUT: 
    #   -portfolio(Portfolio); a user portfolio
    #   -head_length(int); length of the string(head) we are centering under
    # OUTPUT:
    #   -centered_table(str); an adjusted table generated from tabulate
    # PRECONDITION:
    #   -portfolio; fully populated and up to date
    # POSTCONDITION:
    #   -centered_table; a tabulate table is produced with padding to center it under some head
    # RAISES: None
    def construct_stock_table(self, portfolio, head_length : int) -> str:
        stock_list = list(portfolio.stocks.values())

        data = [[stock.ticker, stock.quantity] for stock in stock_list]
        headers = ["Stock", "Quantity"]

        table = tabulate(data, headers = headers, tablefmt="pretty")

        centered_table = "\n".join(line.center(head_length) for line in table.splitlines())

        return centered_table


    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -self.fig; an active chart exists
    # POSTCONDITION:
    #   -self.fig; chart is closed and removed from display
    # RAISES: None
    def close_chart(self) -> None:
        if self.ani is not None:
            self.ani.event_source.stop()
        plt.close(self.fig)
        self.clean_up()
    
    # INPUT:
    #    -event(CloseEvent); matplotlib state in event of manual user closure
    # OUTPUT: None
    # PRECONDITION: None
    # POSTCONDITION:
    #    -self.fig, self.ax, self.ani; all set to None
    # RAISES: None
    def clean_up(self, event : CloseEvent = None) -> None:
        if self.ani is not None:
            self.ani.event_source.stop()
        self.ani = None
        self.fig = None
        self.ax = None
