import time

import serial
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

do_plot = True


def quit (self):
    print ("QUIT")
    exit()


def start_stop (self):
    global do_plot
    global start_stop_txt
    if do_plot:
        do_plot = False
    else:
        do_plot = True


device = serial.Serial(
    port='COM16',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

plt.ion()

figure=plt.figure()
axquit = figure.add_axes([0.81, 0.05, 0.1, 0.075])
bquit = Button(axquit, 'Quit')
axstop = figure.add_axes([0.5, 0.05, 0.28, 0.075])
bstop = Button(axstop, "Start/stop plotting vector")
bquit.on_clicked(quit)
bstop.on_clicked(start_stop)
ax3 = figure.add_subplot(425)
ax2 = figure.add_subplot(422)
ax = figure.add_subplot(421, projection='3d')

time=np.arange(0, 50)
X=np.zeros(50)
Y=np.zeros(50)
Z=np.zeros(50)
values=np.zeros(50)
line2, =ax2.plot(time, values)
line3, =ax3.plot(time, X, color='r')
line4, =ax3.plot(time, Y, color='g')
line5, =ax3.plot(time, Z, color='b')
n=0
axes=["X", "Y", "Z"]
so_far_biggest=[0.0,0.0,0.0]
while 1:
    read = device.readline()
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
    v = [x, y, z]
    absv = [np.abs(x), np.abs(y), np.abs(z)]

    magnitude = np.power(x, 2) + np.power(y, 2) + np.power(z, 2)
    magnitude = np.float_power(magnitude, 0.5)
    magnitude = np.around(magnitude, 2)

    if n==49:
        n=-1
    n+=1
    values=np.roll(values, 1)
    X=np.roll(X,1)
    Y=np.roll(Y,1)
    Z=np.roll(Z,1)
    values[0]=magnitude
    X[0]=x
    Y[0]=y
    Z[0]=z
    if absv[0]>so_far_biggest[0]:
        so_far_biggest[0]=absv[0]
    if absv[1]>so_far_biggest[1]:
        so_far_biggest[1]=absv[1]
    if absv[2]>so_far_biggest[2]:
        so_far_biggest[2]=absv[2]

    colorchar = 'b'

    # determine the biggest
    index = np.argmax(absv)
    if v[index] < 0:
        colorchar = 'r'

    status = "stationary"
    if magnitude > 10.1 or magnitude < 9:
        status = "external force applied"

    ax.clear()
    plt.subplot (421)
    plt.title("Vector representation", fontsize=9)
    plt.xlabel("X-axis", fontsize=9)
    plt.ylabel("Y-axis", fontsize=9)

    ax.set_xlim([10, -10])
    ax.set_ylim([10, -10])
    ax.set_zlim([10, -10])
    ax.set_zlabel("Z-axis")

    plt.subplot(422)
    plt.title ("Magnitude over measurements", fontsize=9)
    plt.xlabel("Measurements ago \n" + "\nRead (x, y, z): " + line + " [m/s\u00b2]\n" + "Status: " + status + "\nMagnitude: " + str(
        magnitude) + " [m/s\u00b2]" + "\nBiggest acceleration at axis: " + axes[index] + "\nSo far biggest: " + "x=" + str(so_far_biggest[0])
               + " y=" + str(so_far_biggest[1]) + "z= " + str(so_far_biggest[2]), fontsize = 9)
    plt.ylabel("Acceleration [m/s\u00b2]", fontsize=9)
    ax2.set_xlim([0, 50])
    ax2.set_ylim([0, 40])
    plt.subplot(425)
    plt.title ("x, y and z acceleration over measurements", fontsize=9)
    plt.xlabel("Measurements ago\nX: red, Y: green, Z: blue", fontsize=9)
    ax3.set_xlim([0, 50])
    ax3.set_ylim([-20, 20])

    line2.set_ydata(values)
    line3.set_ydata(X)
    line4.set_ydata(Y)
    line5.set_ydata(Z)

    if do_plot:
        line1 = ax.quiver(0, 0, 0, x, y, z, color=colorchar)
    figure.canvas.flush_events()
