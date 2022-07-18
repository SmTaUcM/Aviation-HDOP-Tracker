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
        self.gridLineSeperation = 1

        # Main program logic.
        filePath = openFile()
        if filePath != "":
            self.gpsData = self.readGPSData(filePath)
            self.gpsData = self.filterData(self.gpsData)
            self.gpsData = self.appendDecimalCoords(self.gpsData)

            # Render the output map and plot to the user.
            self.middleLat, self.middleLong, self.lLong, self.hLong, self.lLat, self.hLat = findCenter(self.gpsData)
            self.displayMapPlot()
        #--------------------------------------------------------------------------------------------------------------------------------------------#

    def displayMapPlot(self):
        '''Method to render a map and aircraft track data as per the selected GPS log file.'''

        # Apply default map settings.
        plt.rcParams["figure.figsize"] = self.windowSize
        plt.get_current_fig_manager().canvas.set_window_title(self.mainWindowTitle)
        plt.get_current_fig_manager().canvas.toolbar.zoom()
        plt.title("Aircraft GPS Track (HDOP > 2.0 shown in red)")  # Map title.

        # Define a Lambert Conformal Conic map.
        self.mapPlot = Basemap(width=3000000, height=2000000,
                               rsphere=(6378137.00, 6356752.3154),
                               projection='lcc', lat_1=1.0, lat_2=2,
                               lat_0=self.middleLat, lon_0=self.middleLong,
                               resolution='l', area_thresh=1000.0)

        # Draw coastlines, meridians and parallels onto the map.
        self.mapPlot.drawcoastlines()
        self.mapPlot.drawcountries()
        self.mapPlot.drawrivers()
        self.mapPlot.drawmapboundary(fill_color=self.waterColour)
        self.mapPlot.fillcontinents(color=self.landColour, lake_color=self.waterColour)
        self.mapPlot.drawparallels(np.arange(-90, 90, self.gridLineSeperation), labels=[False, True, True, False])
        self.mapPlot.drawmeridians(np.arange(-180, 180, self.gridLineSeperation), labels=[False, False, False, True])

        # Draw the aircraft's track and DHOP data.
        self.plotAircraftTrack(self.gpsData)

# Zoom in on the aircraft track area.
# self.mapPlot(Long, Lat) Converts decimal Lat/Long degrees in to Meters, needed by Basemap for drawing.
##        bottomLeft = self.mapPlot(self.lLong, self.lLat)
##        topRight = self.mapPlot(self.hLong, self.hLat)
##        xPadding = (topRight[0] - bottomLeft[0]) * 0.25
##        yPadding = (topRight[1] - bottomLeft[1]) * 0.25
##        plt.axis([bottomLeft[0] - xPadding, topRight[0] + xPadding, bottomLeft[1] - yPadding, topRight[1] + xPadding])

        # Show the output.
        plt.show()
        #--------------------------------------------------------------------------------------------------------------------------------------------#

    def readGPSData(self, filePath):
        '''Method to read in the GPS Log data and store it as a list of dictionaries.

        readGPSData() --> [{"GPRMC" : [,,"V",,,,,,,,,,"N*53"], "GPVTG" : [,,,,,,,,,"N*30"]}]'''

        # Read in the raw GPS Log data.
        rawData = []
        with open(filePath, "r") as dataFile:
            rawData = dataFile.readlines()

        # Store the date into a series of nested lists. Easch nest represents a message sequence.
        data = []
        message = []
        for line in rawData:
            entry = line.replace("\n", "").split(",")
            if entry[0][:2] == "GP" or entry[0][:3] == "$GP":  # Check for NEMA message identifier. e.g. "GPRMC"
                message.append(entry)

            # If the last entry in the message sequence is reached. Save our data and create a new message.
            if entry[0] == "GPGGA" or entry[0] == "$GPGGA":
                data.append(message)
                message = []

        return data
        #--------------------------------------------------------------------------------------------------------------------------------------------#

    def filterData(self, data):
        '''Method for filtering GPS Log data so that only valid messages are present with the data points that we require.'''

        # Filter for the data points that we require. i.e.
        # $GPGGA (Global Positioning System Fix Data) :
        #   Index 0       = Interpreted sentences
        #   Indexes 2 & 3 = Latitude
        #   Indexes 4 & 5 = Longitude,
        #   Index 6       = GPS quality indicator (0=invalid; 1=GPS fix; 2=Diff. GPS fix)
        #   Index 8       = HDOP (Horizontal dilution of position)

        SENTENCE_ID = 0
        GPS_QUALITY = 6

        filteredData = []
        for message in data:
            for entry in message:
                if entry[SENTENCE_ID] == "GPGGA" or entry[SENTENCE_ID] == "$GPGGA":
                    if entry[GPS_QUALITY] != "":
                        if int(entry[GPS_QUALITY]) > 0:
                            filteredData.append(entry)

        return filteredData
        #--------------------------------------------------------------------------------------------------------------------------------------------#

    def appendDecimalCoords(self, data):
        '''Method for adding decimal lat/long values to the end of each GPS Log $GPGGA filtered message.'''

        LAT_VALUE = 2
        LAT_DIR = 3
        LONG_VALUE = 4
        LONG_DIR = 5

        newData = []
        for message in data:
            newMessage = message + [convertToDegrees(message[LAT_VALUE], message[LAT_DIR]), convertToDegrees(message[LONG_VALUE], message[LONG_DIR])]
            newData.append(newMessage)

        return newData
        #--------------------------------------------------------------------------------------------------------------------------------------------#

    def plotAircraftTrack(self, data):
        '''Method used to plot the filtered and appeneded NEMA GPS Log data onto the map.'''

        # Declare local constants.
        LAT = 15
        LONG = 16
        HDOP = 8
        HDOP_GOOD = "#00FF00"
        HDOP_BAD = "#FF0000"

        # Draw the map's center point.
        long, lat = self.mapPlot(self.middleLong, self.middleLat)
        self.mapPlot.plot(long, lat, color="#111111", marker='+')

        # Create a list contining meters converted lat / long along with our HDOP figure..
        plots = []
        for message in self.gpsData:
            # self.mapPlot(Long, Lat) Converts decimal Lat/Long degrees in to Meters, needed by Basemap for drawing.
            plots.append([self.mapPlot(message[LONG], message[LAT]), message[HDOP]])

        # Dertermine if DHOP is within tolerance and then plot the current fix to the next upon the map.
        for plot in range(len(plots) - 1):
            if plot == range(len(plots) - 1):  # Prevent iterating beyond our list.
                break
            else:
                if float(plots[plot][1]) > 2.0:
                    lineCol = HDOP_BAD
                else:
                    lineCol = HDOP_GOOD

                self.mapPlot.plot([plots[plot][0][0], plots[plot + 1][0][0]], [plots[plot][0][1], plots[plot + 1][0][1]], color=lineCol)
        #--------------------------------------------------------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------#


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


def convertToDegrees(gpsLogCoords, nsew):
    '''Function that takes a NEMA GPS Log formatted lattitude or longitude and converts it to decimal degrees.

    e.g. convertToDegrees("5126.5", "N") --> float(51.44166666666667)'''

    if nsew in ["N", "S"]:  # Calculating Latitude
        degs, mins = gpsLogCoords[:2], gpsLogCoords[2:]
    elif nsew in ["E", "W"]:  # Calculating Longitude
        degs, mins = gpsLogCoords[:3], gpsLogCoords[3:]

    decimalDegs = float(degs) + (float(mins) / 60)
    if nsew in ["S", "W"]:
        decimalDegs = 0 - decimalDegs
    return decimalDegs
    #------------------------------------------------------------------------------------------------------------------------------------------------#


def findCenter(data):
    '''Function that will identify and return the central and extreme Lat/Long CoOrds of a given list of $GPGGA
       filtered and appended NEMA GPS Log Data.'''

    # Declare local constants.
    LAT = 15
    LONG = 16

    # Declare local variables.
    lowestLat = 90.0
    highestLat = -90.0
    lowestLong = 180.0
    highestLong = -180.0

    # Find the highest and lowest lat/longs.
    for message in data:
        if message[LONG] < lowestLong:
            lowestLong = message[LONG]
        if message[LONG] > highestLong:
            highestLong = message[LONG]
        if message[LAT] < lowestLat:
            lowestLat = message[LAT]
        if message[LAT] > highestLat:
            highestLat = message[LAT]

    middleLat = ((highestLat - lowestLat) / 2) + lowestLat
    middleLong = ((highestLong - lowestLong) / 2) + lowestLong

    return middleLat, middleLong, lowestLong, highestLong, lowestLat, highestLat
    #------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                     Main Program.                                                                  #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
hdopTracker = HdopTracker()
#----------------------------------------------------------------------------------------------------------------------------------------------------#
