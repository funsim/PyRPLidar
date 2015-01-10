A Python library for accessing an RPLidar device.

Install

    git clone https://github.com/funsim/PyRPLidar.git
    cd PyRPLidar
    sudo python setup.py install

```python
from rplidar import *

# Find and connect to the RP Lidar
port = find_rplidar_port()
rplidar = RPLidar(port)
rplidar.connect()

# Get some status information
print rplidar.get_device_info()
print rplidar.get_health()

# Start the lidar measurements
rplidar.start_monitor(archive=True)

# Read and plot measurements until the user presses a key
plot = XYPlot()
while True:
    plot.update(rplidar.current_frame)
```
