import matplotlib.pyplot as plt
import pandas as pd


# PURPOSE:
class Visualizer:

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        
    # INPUT:
    # OUTPUT:
    # PRECONDITION:
    # POSTCONDITION:
    def display_pie_chart(self, raw_holdings_data):
        # TODO: use pandas to format the data
        # TODO: use matplotlib to display the data

        plt.show(block=False) #Displays chart doesnt block program
        self.fig.canvas.draw() #Redraws chart