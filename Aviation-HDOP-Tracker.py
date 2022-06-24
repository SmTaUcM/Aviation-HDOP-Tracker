import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Default map settings.
mLat, mLong = 54.5, -4.0
plt.rcParams["figure.figsize"] = [16, 12]
plt.get_current_fig_manager().canvas.set_window_title("Aviation HDOP Plotter")

# Define a Lambert Conformal Conic map.
m = Basemap(width=3000000, height=2000000,
            rsphere=(6378137.00, 6356752.3154),
            projection='lcc', lat_1=1.0, lat_2=2, lat_0=mLat, lon_0=mLong,
            resolution='l', area_thresh=1000.0)

# Draw coastlines, meridians and parallels onto the map.
m.drawcoastlines()
m.drawcountries()
m.drawrivers()
m.drawmapboundary(fill_color='#181f69')
m.fillcontinents(color='#2e632f', lake_color='#181f69')
m.drawparallels(np.arange(-90, 90, 5), labels=[False, True, True, False])
#                          beg, end, step                     lblTop, lblBot
m.drawmeridians(np.arange(-180, 180, 5), labels=[False, False, False, True])
plt.title("Aircraft GPS Track (HDOP >= 2.0 shown in red)")

# Draw the map's center point.
long, lat = m(mLong, mLat)
m.plot(long, lat, color="#00FF00", marker='o')

# Plot a track on the map.
plots = []
plots.append(m(-0.172765, 53.104912))  # Conz - Long / Lat
plots.append(m(-3.315890, 57.663363))  # Loss
plots.append(m(-1.973986, 51.500667))  # Lyn

for plot in range(len(plots) - 1):
    if plot == range(len(plots) - 1):  # Prevent iterating beond our list.
        break
    else:
        m.plot([plots[plot][0], plots[plot + 1][0]], [plots[plot][1], plots[plot + 1][1]], color="#FF0000")

# Show the output.
plt.show()
