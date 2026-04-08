import matplotlib.pyplot as plt
import pandas as pd


# PURPOSE:
#   -Visualizer provides a data visualization abstraction
#   -provides an isolated layer that allows for construction of data charts
class Visualizer:
        
    # INPUT:
    #   -portfolio_data(list[dict[str|int]]); formatted portfolio data
    # OUTPUT: None
    # PRECONDITION:
    #   -portfolio_data; non-empty, each dict contains 'ticker'(str) and 'quantity'(int)
    # POSTCONDITION:
    #   -self.fig; pie chart rendered with ticker labels and quantity distribution
    #   -execution; chart display does not block program
    # RAISES: None
    def display_pie_chart(self, portfolio_data : list[dict[str, str | int]]) -> None:
        if not portfolio_data:
            return

        df = pd.DataFrame(portfolio_data)

        self.fig, self.ax = plt.subplots()

        self.ax.pie(df['quantity'], labels=df['ticker'], autopct='%1.0f%%')
        self.ax.set_title("Portfolio Distribution")

        plt.show(block=False)  
        plt.pause(0.1)          

    
    # INPUT: None
    # OUTPUT: None
    # PRECONDITION:
    #   -self.fig; an active chart exists
    # POSTCONDITION:
    #   -self.fig; chart is closed and removed from display
    # RAISES: None
    def close_chart(self) -> None:
        if hasattr(self, "fig"):
            plt.close(self.fig)