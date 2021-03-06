"""
RPLidar Python Driver

...
...

"""

import os
import serial
import logging
import Queue
import numpy
from collections import deque
import matplotlib.pyplot as plt

from rplidar_monitor import *

class Frame(object):
    def __init__(self, xin, yin):
        try:
            self.x = numpy.average(xin, axis=0)
            self.y = numpy.average(yin, axis=0)
        except:
            print "Warning: No points yet"
            self.x = numpy.zeros(360)
            self.y = numpy.zeros(360)


class FloorMap(object):
    """ Stores the floor plan of the measurements based on a moving average. """

    def __init__(self):
        self.measurements_x = []
        self.measurements_y = []

    def add_measurement(self, x, y):
        assert len(x) == len(y)
        if len(x) == 360:
            self.measurements_x.append(numpy.array(x))
            self.measurements_y.append(numpy.array(y))
        else:
            print "Warning: Ignore incomplete data."

        print "Number of measurements ", len(self.measurements_x)

    def get_average(self):
        return Frame(self.measurements_x, self.measurements_y)


class RPLidar(object):

    def __init__(self, portname, baudrate=115200, timeout=1):

        # init serial port
        self.serial_port = None
        self.portname = portname
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_arg = dict(port=portname,
                               baudrate=baudrate,
                               stopbits=serial.STOPBITS_ONE,
                               parity=serial.PARITY_NONE,
                               timeout=timeout)

        # status variables
        self.isConnected = False
        self.motorRunning = None

        # init monitor
        self.monitor = None

        # data containers
        self.raw_points = Queue.Queue()
        self.raw_frames = Queue.Queue()
        self.current_frame = RPLidarFrame()


    def connect(self):

        if not self.isConnected:
            try:
                self.serial_port = serial.Serial(**self.serial_arg)
                self.isConnected = True
                logging.debug("Connected to RPLidar on port %s", self.portname)
                self.stop_motor()
            except serial.SerialException as e:
                logging.error(e.message)


    def disconnect(self):

        if self.isConnected:
            try:
                if self.monitor:
                    self.stop_monitor()
                self.serial_port.close()
                self.isConnected = False
                logging.debug("Disconnected from RPLidar on port %s", self.portname)
            except serial.SerialException as e:
                logging.error(e.message)


    def reset(self):

        self.send_command(RPLIDAR_CMD_RESET)
        logging.debug("Command RESET sent.")
        time.sleep(0.1)


    def start_motor(self):
        """Start RPLidar motor by setting DTR (which is connected to pin MOTOCTL
        on RPLidar) to False."""

        self.serial_port.setDTR(False)
        self.motorRunning = True
        logging.debug("RPLidar motor is turned ON.")


    def stop_motor(self):
        """Stop RPLidar motor by setting DTR to True."""

        self.serial_port.setDTR(True)
        self.motorRunning = False
        logging.debug("RPLidar motor is turned OFF.")


    def send_command(self, command):
        """Send command to RPLidar through the serial connection"""

        cmd_bytes = rplidar_command_format.build(Container(
                             sync_byte=RPLIDAR_CMD_SYNC_BYTE, cmd_flag=command))
        self.serial_port.write(cmd_bytes)
        logging.debug("Command %s sent.", toHex(cmd_bytes))


    def response_header(self, timeout=1):
        """Read response header from RPLidar through the serial connection"""

        start_time = time.time()

        while time.time() < start_time + timeout:
            if self.serial_port.inWaiting() < rplidar_response_header_format.sizeof():
                #logging.debug(serial_port.inWaiting())
                time.sleep(0.01)
            else:
                raw = self.serial_port.read(rplidar_response_header_format.sizeof())
                parsed = rplidar_response_header_format.parse(raw)
                #logging.debug(parsed)

                if ((parsed.sync_byte1 != RPLIDAR_ANS_SYNC_BYTE1) or
                    (parsed.sync_byte2 != RPLIDAR_ANS_SYNC_BYTE2)):
                    raise RPLidarError("RESULT_INVALID_ANS_HEADER")
                else:
                    return parsed.response_type

        raise RPLidarError("RESULT_READING_TIMEOUT")


    def get_device_info(self):
        """Obtain hardware information about RPLidar"""

        self.serial_port.flushInput()

        self.send_command(RPLIDAR_CMD_GET_DEVICE_INFO)

        if self.response_header() == RPLIDAR_ANS_TYPE_DEVINFO:
            raw = self.serial_port.read(rplidar_response_device_info_format.sizeof())
            parsed = rplidar_response_device_info_format.parse(raw)

            return {"model": parsed.model,
                    "firmware_version_major": parsed.firmware_version_major,
                    "firmware_version_minor": parsed.firmware_version_minor,
                    "hardware_version": parsed.hardware_version,
                    "serial_number": toHex(parsed.serial_number)}

        else:
            raise RPLidarError("RESULT_INVALID_ANS_TYPE")


    def get_health(self):
        """Obtain health information about RPLidar"""

        self.serial_port.flushInput()

        self.send_command(RPLIDAR_CMD_GET_DEVICE_HEALTH)

        if self.response_header() == RPLIDAR_ANS_TYPE_DEVHEALTH:
            raw = self.serial_port.read(rplidar_response_device_health_format.sizeof())
            parsed = rplidar_response_device_health_format.parse(raw)

            return {"status": parsed.status,
                    "error_code": parsed.error_code}
        else:
            raise RPLidarError("RESULT_INVALID_ANS_TYPE")


    def start_monitor(self, archive=False):
        """ Start the monitor thread """

        if self.monitor is None:
            logging.debug("Try to start monitor thread.")
            self.monitor = RPLidarMonitor(self, archive=archive)
            self.monitor.start()


    def stop_monitor(self):
        """ Stop the monitor """

        if self.monitor is not None:
            logging.debug("Try to stop monitor thread.")
            self.monitor.join()
            self.monitor = None



class PolarPlot(object):
    def __init__(self):
        """ setup a polar plot canvas """

        plt.ion()
        self.figure = plt.figure(figsize=(6, 6),
                                 dpi=160,
                                 facecolor="w",
                                 edgecolor="k")
        self.ax = self.figure.add_subplot(111, polar=True)
        self.lines, = self.ax.plot([],[],
                                   linestyle="none",
                                   marker=".",
                                   markersize=3,
                                   markerfacecolor="blue")
        self.ax.set_rmax(5000)
        self.ax.set_theta_direction(-1) #set to clockwise
        self.ax.set_theta_offset(numpy.pi/2) #offset by 90 degree so that 0 degree is at 12 o'clock
        #self.ax.grid()


    def update(self, current_frame):
        """ re-draw the polar plot with new current_frame """

        self.lines.set_xdata(current_frame.angle_r)
        self.lines.set_ydata(current_frame.distance)
        self.figure.canvas.draw()


class XYPlot(object):
    def __init__(self):
        """ setup an XY plot canvas """

        plt.ion()
        self.figure = plt.figure(figsize=(6, 6),
                                 dpi=160,
                                 facecolor="w",
                                 edgecolor="k")
        self.ax = self.figure.add_subplot(111)
        self.lines, = self.ax.plot([],[],
                                   linestyle="-",
                                   marker=".",
                                   markersize=3,
                                   markerfacecolor="blue")
        self.origin, = self.ax.plot([],[],
                                    marker="x",
                                    markerfacecolor="black")
        self.ax.set_xlim(-5000, 5000)
        self.ax.set_ylim(-5000, 5000)
        self.ax.grid()


    def update(self, current_frame):
        """ re-draw the XY plot with new current_frame """

        x = list(current_frame.x)
        y = list(current_frame.y)

        # Filter out invalid rplidar measurements
        filterx = []
        filtery = []
        tol = 1e-1
        for xx, yy in zip(x, y):
            if not (abs(xx) < tol and abs(yy) < tol):
                filterx.append(xx)
                filtery.append(yy)


        self.lines.set_xdata(filterx)
        self.lines.set_ydata(filtery)
        try:
            self.origin.set_xdata(filterx[0])
            self.origin.set_ydata(filtery[0])
        except:
            pass

        self.figure.canvas.draw()

def find_rplidar_port():
    """ Attempts to identify the RPlidar USB port by polling common names. """
    import platform

    # Windows
    if platform.system() == "Windows":
        return "COM3"

    # Mac and Linux
    suspects = ["/dev/ttyUSB0", "/dev/tty.SLAB_USBtoUART"]
    for f in suspects:
        print "trying ", f
        if os.path.exists(f):
            return f
    raise IOError, "No RPLidar device was found."


if __name__ == "__main__":

    # logging config
    logging.basicConfig(level=logging.DEBUG,
                    format="[%(levelname)s] (%(threadName)-10s) %(message)s")

    port = find_rplidar_port()
    rplidar = RPLidar(port)
    rplidar.connect()


    print rplidar.get_device_info()
    print rplidar.get_health()

    rplidar.start_monitor(archive=True)

    plot = PolarPlot()
    #floor_map = FloorMap()

    try:
        while True:

            #x = rplidar.current_frame.x
            #y = rplidar.current_frame.y
            #floor_map.add_measurement(x, y)

            plot.update(rplidar.current_frame)
            time.sleep(0.15)

    except KeyboardInterrupt:
        logging.debug("CTRL-c pressed, exiting...")
        pass

    rplidar.stop_monitor()
    rplidar.disconnect()
    rplidar = None
