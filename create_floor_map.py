"""
Read the RPLidar and stores a floor map as a text file in the format

xmin xmax ymin ymax
x1 y1
x2 y2
x3 y1

Here the x* variables are floating point numbers.
"""

import sys
import logging
import time
import select
from rplidar import RPLidar, XYPlot


def filter_frame(x, y):
    """ Filters invalid points from the current frame """
    xfilt = []
    yfilt = []

    for xx, yy in zip(x, y):
        if abs(xx) + abs(yy) < 1e-3:
            continue
        xfilt.append(xx)
        yfilt.append(yy)
    return xfilt, yfilt

# Set logging setup
logging.basicConfig(level=logging.DEBUG,
                format="[%(levelname)s] (%(threadName)-10s) %(message)s")

rplidar = RPLidar("/dev/ttyUSB0")
rplidar.connect()

print rplidar.get_device_info()
print rplidar.get_health()

# Start the lidar measurements
rplidar.start_monitor(archive=True)

# Read and plot measurements until the user presses a key
plot = XYPlot()
while True:
    plot.update(rplidar.current_frame)

    i, o, e = select.select( [sys.stdin], [], [], 0.15 )
    if i:
        break
x = rplidar.current_frame.x
y = rplidar.current_frame.y

x, y = filter_frame(x, y)

# Write data to file
file_ = open('point_file.txt', 'w')
# Write bounding box
file_.write('{} {} {} {}\n'.format(min(x), max(x),
                                 min(y), max(y)))
# Write all x,y tuples
for xx, yy in zip(x, y):
    file_.write("{} {}\n".format(xx, yy))
file_.close()


rplidar.stop_monitor()
rplidar.disconnect()
rplidar = None
