import serial  # library for connecting to a device
import numpy as np  # all the calculations are done with numpy library
from matplotlib import pyplot as plt  # we plot with matplotlib library
from matplotlib.widgets import Button  # matplotlib contains buttons so we do not need an external library
import sys  # to get command line argument

do_plot = True  # variable which contains boolean whether to plot 3D vector or not
port_name = 'COM16'  # the name of the port to which our device is connected to


# function which enables or disables 3D vector plotting hence it is resource intensive
def start_stop(self):
    global do_plot
    if do_plot:
        do_plot = False
    else:
        do_plot = True


# if a command line argument is given - take it as the port name, otherwise use the default
if len(sys.argv) == 2:
    port_name = str(sys.argv[1])

# declare an object of a serial class device, connect to device with given serial port name
device = serial.Serial(
    port=port_name,
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# enables interactive mode
plt.ion()

# add a figure to the plot
figure = plt.figure()
# add buttons
axquit = figure.add_axes([0.81, 0.05, 0.1, 0.075])
breset = Button(axquit, 'Reset')
axstop = figure.add_axes([0.5, 0.05, 0.28, 0.075])
bstop = Button(axstop, "Start/stop plotting vector")
bstop.on_clicked(start_stop)

# add figures to the plot, one row as a separator
ax_xyz = figure.add_subplot(425)  # x, y, z over measurements
ax_magnitude = figure.add_subplot(422)  # magnitude over measurements
ax_vect = figure.add_subplot(421, projection='3d')  # 3D vector projection

time = np.arange(0, 50)  # time is actually an array storing integers from 0 to 49 representing following measurements
X = np.zeros(50)  # vector for storing measurements of x axis acceleration
Y = np.zeros(50)  # vector for storing measurements of y axis acceleration
Z = np.zeros(50)  # vector for storing measurements of z axis acceleration
values = np.zeros(50)  # vector for storing measurements of magnitude of acceleration

magnitude_line, = ax_magnitude.plot(time, values)  # viewing magnitude plot
x_line, = ax_xyz.plot(time, X, color='r')  # viewing plot of x axis measurement
y_line, = ax_xyz.plot(time, Y, color='g')  # viewing plot of y axis measurement
z_line, = ax_xyz.plot(time, Z, color='b')  # viewing plot of z axis measurement

axes = ["X", "Y", "Z"]  # axes labels array
so_far_biggest = [0.0, 0.0, 0.0]  # array for storing the biggest read of values


# reset all the measurements
def reset(self):
    global X
    global Y
    global Z
    global values
    global so_far_biggest
    so_far_biggest = [0.0, 0.0, 0.0]  # array for storing the biggest read of values
    X = np.zeros(50)  # vector for storing measurements of x axis acceleration
    Y = np.zeros(50)  # vector for storing measurements of y axis acceleration
    Z = np.zeros(50)  # vector for storing measurements of z axis acceleration
    values = np.zeros(50)  # vector for storing measurements of magnitude of acceleration


def roll_values():
    global X
    global Y
    global Z
    global values
    values = np.roll(values, 1)
    X = np.roll(X, 1)
    Y = np.roll(Y, 1)
    Z = np.roll(Z, 1)


def insert_at_zero(x, y, z, magnitude):
    global X
    global Y
    global Z
    global values
    values[0] = magnitude
    X[0] = x
    Y[0] = y
    Z[0] = z

def calc_magnitude (x, y, z):
    magnitude = np.power(x, 2) + np.power(y, 2) + np.power(z, 2)
    magnitude = np.float_power(magnitude, 0.5)
    magnitude = np.around(magnitude, 2)
    return magnitude


breset.on_clicked(reset)
while 1:
    read = device.readline()  # read from the device

    # split the read line into separate float variables and concatenate string variables in a more human friendly format
    line = str(read)
    line = line.split('\'', 1)[1]
    line = line.split('\\', 1)[0]
    sx = line.split(' ', 1)[0]
    rest = line.split(' ', 1)[1]
    sy = rest.split(' ', 1)[0]
    sz = rest.split(' ', 1)[1]
    line = sx + ", " + sy + ", " + sz
    x = float(sx)
    y = float(sy)
    z = float(sz)

    v = [x, y, z]  # store x, y and z axis read in an array, easier to use in some cases
    absv = [np.abs(x), np.abs(y), np.abs(z)]  # absolute values of readings,
    # used to determine the biggest component vector - an index is more useful than making it an if
    # statement, hence the array

    # calculate the magnitude
    magnitude = calc_magnitude(x,y,z)

    # present the data on a chart - shift an array so the last reading becomes the first, the first the second,
    # etc. then replace the first (past last)
    roll_values()
    insert_at_zero(x, y, z, magnitude)

    # check if reading is bigger than previous readings
    if absv[0] > so_far_biggest[0]:
        so_far_biggest[0] = absv[0]
    if absv[1] > so_far_biggest[1]:
        so_far_biggest[1] = absv[1]
    if absv[2] > so_far_biggest[2]:
        so_far_biggest[2] = absv[2]

    colorchar = 'b'  # char used to determine colour of the 3D vector - blue biggest positive, red biggest negative

    # determine the biggest component vector
    index = np.argmax(absv)
    if v[index] < 0:
        colorchar = 'r'  # if biggest is negative, then make the vector red

    status = "stationary"  # if detected acceleration is bigger than g, an external force must have been applied -
    # - change the status text
    if magnitude > 10.1 or magnitude < 9:
        status = "external force applied"

    # clear the vector representation plot and make titles
    ax_vect.clear()
    plt.subplot(421)
    plt.title("Vector representation", fontsize=9)
    plt.xlabel("X-axis", fontsize=9)
    plt.ylabel("Y-axis", fontsize=9)

    ax_vect.set_xlim([10, -10])
    ax_vect.set_ylim([10, -10])
    ax_vect.set_zlim([10, -10])
    ax_vect.set_zlabel("Z-axis")

    # set titles for magnitude and x y z plots
    plt.subplot(422)
    plt.title("Magnitude over measurements", fontsize=9)
    plt.xlabel(
        "Measurements ago \n" + "\nRead (x, y, z): " + line + " [m/s\u00b2]\n" + "Status: " + status + "\nMagnitude: " + str(
            magnitude) + " [m/s\u00b2]" + "\nBiggest acceleration at axis: " + axes[
            index] + "\nSo far biggest: " + "x=" + str(so_far_biggest[0])
        + " y=" + str(so_far_biggest[1]) + "z= " + str(so_far_biggest[2]), fontsize=9)
    plt.ylabel("Acceleration [m/s\u00b2]", fontsize=9)
    ax_magnitude.set_xlim([0, 50])
    ax_magnitude.set_ylim([0, 40])
    plt.subplot(425)
    plt.title("x, y and z acceleration over measurements", fontsize=9)
    plt.xlabel("Measurements ago\nX: red, Y: green, Z: blue", fontsize=9)
    ax_xyz.set_xlim([0, 50])
    ax_xyz.set_ylim([-20, 20])

    # update plots data
    magnitude_line.set_ydata(values)
    x_line.set_ydata(X)
    y_line.set_ydata(Y)
    z_line.set_ydata(Z)

    # if plotting 3D vector enabled, then plot it
    if do_plot:
        line1 = ax_vect.quiver(0, 0, 0, x, y, z, color=colorchar)
    figure.canvas.flush_events()
