'''#-------------------------------------------------------------------------------------------------------------------------------------------------#
# Name:        Aviation-HDOP-Tracker.py
# Purpose:     From a GPS log, provides a visual Latitude/Longitude plot of an aircraft track. The plot will indicate portions of the flight where
#              the Horizontal Dilution of Precision (HDOP) was high.
#
# Version:     v0.01 Alpha
# Author:      Stuart Macintosh
#
# Created:     24/06/2022
# Copyright:   Stuart Macintosh 2022
# Licence:     GNU v3
#
# Developed using Python v3.8.7 32-bit.
# External dependencies are commented. Imports with no comments are included with the regular Python installation.
#-------------------------------------------------------------------------------------------------------------------------------------------------#'''

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                      Imports.                                                                      #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
import os
import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
# Requires download from https://github.com/matplotlib/basemap/releases/ then run:
# python -m pip install basemap-data
# python -m pip install basemap-data-hires
# python -m pip install basemap
#----------------------------------------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                      Classes.                                                                      #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
class HdopTracker():
    '''Container object representing our Aviation HDOP Plotter'''

    def __init__(self):
        '''Container object representing our Aviation HDOP Plotter'''

        # Declare default instance variables.
        self.middleLat, self.middleLong = 54.5, -4.0  # Lat/Long for UK.
        self.windowSize = [16, 12]
        self.mainWindowTitle = "Aviation HDOP Plotter"
        self.landColour = "#2e632f"
        self.waterColour = "#181f69"
        self.gridLineSeperation = 5
        self.gpsFile = openFile()

        # Render the output map and plot to the user.
        self.displayMapPlot()
        #--------------------------------------------------------------------------------------------------------------------------------------------#

    def displayMapPlot(self):
        '''Method to render a map and aircraft track data as per the selected GPS log file.'''

        # Apply default map settings.
        plt.rcParams["figure.figsize"] = self.windowSize
        plt.get_current_fig_manager().canvas.set_window_title(self.mainWindowTitle)
        plt.title("Aircraft GPS Track (HDOP >= 2.0 shown in red)")  # Map title.

        # Define a Lambert Conformal Conic map.
        mapPlot = Basemap(width=3000000, height=2000000,
                          rsphere=(6378137.00, 6356752.3154),
                          projection='lcc', lat_1=1.0, lat_2=2,
                          lat_0=self.middleLat, lon_0=self.middleLong,
                          resolution='l', area_thresh=1000.0)

        # Draw coastlines, meridians and parallels onto the map.
        mapPlot.drawcoastlines()
        mapPlot.drawcountries()
        mapPlot.drawrivers()
        mapPlot.drawmapboundary(fill_color=self.waterColour)
        mapPlot.fillcontinents(color=self.landColour, lake_color=self.waterColour)
        mapPlot.drawparallels(np.arange(-90, 90, self.gridLineSeperation), labels=[False, True, True, False])
        mapPlot.drawmeridians(np.arange(-180, 180, self.gridLineSeperation), labels=[False, False, False, True])

        # -------------- Test Code. ------------------------
        # Draw the map's center point.
        long, lat = mapPlot(self.middleLong, self.middleLat)
        mapPlot.plot(long, lat, color="#00FF00", marker='o')

        # Plot a track on the map.
        plots = []
        plots.append(mapPlot(-0.172765, 53.104912))  # Conz - Long / Lat
        plots.append(mapPlot(-3.315890, 57.663363))  # Loss
        plots.append(mapPlot(-1.973986, 51.500667))  # Lyn

        for plot in range(len(plots) - 1):
            if plot == range(len(plots) - 1):  # Prevent iterating beond our list.
                break
            else:
                mapPlot.plot([plots[plot][0], plots[plot + 1][0]], [plots[plot][1], plots[plot + 1][1]], color="#FF0000")
        # ----------- End of Test Code. --------------------

        # Show the output.
        plt.show()
        #--------------------------------------------------------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                      Functions.                                                                    #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
def openFile():
    '''Function that asks the user to select a file to be read in by this program.

    openFile() --> str(filePath)'''

    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Please select a GPS Log file...", initialdir=os.getcwd(), filetypes=[("Text files", "*.txt")])
    #------------------------------------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                     Main Program.                                                                  #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
hdopTracker = HdopTracker()
