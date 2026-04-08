import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
    #   -portfolio_data(list[dict[str|int]]); formatted portfolio data
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio_data; non-empty, each dict contains 'ticker'(str) and 'quantity'(int)
    # POSTCONDITION:
    #   -self.fig; pie chart rendered with ticker labels and quantity distribution
    #   -execution; chart display does not block program
    # RAISES: None
    def display_pie_chart(self, package_portfolio_data : callable) -> None:
        if not package_portfolio_data():
            return

        self.fig, self.ax = plt.subplots()

        def update(frame):
            portfolio_data = package_portfolio_data()
            df = pd.DataFrame(portfolio_data)

            self.ax.clear()
            self.ax.pie(df['quantity'], labels=df['ticker'], autopct='%1.0f%%')
            self.ax.set_title("Portfolio Distribution")

        self.ani = animation.FuncAnimation(self.fig, update, interval=1000, cache_frame_data=False)
        plt.show(block=False)    

    
    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -self.fig; an active chart exists
    # POSTCONDITION:
    #   -self.fig; chart is closed and removed from display
    # RAISES: None
    def close_chart(self) -> None:
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None