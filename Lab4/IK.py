import numpy as np
from scipy.optimize import fsolve
import time

# Target values and link lengths
X_new, Y_new, Z_new = 307, 6, 31
a1, a2, a4, a3, b3, a5, b5 = 0, 150, 150, 25, 50, 40, 30
print(f"requested X, Y, Z:{X_new}, {Y_new}, {Z_new}")
# Define system of residual equations (Eq - Target = 0)
def equations(q):
    J1, J2, J3 = q
    Px = np.cos(J1) * (a5 + b3 + a4 * np.cos(J3) + a2 * np.sin(J2))
    Py = np.sin(J1) * (a5 + b3 + a4 * np.cos(J3) + a2 * np.sin(J2))
    Pz = a1 + a3 - b5 + a2 * np.cos(J2) - a4 * np.sin(J3) + 5

    return [Px - X_new, Py - Y_new, Pz - Z_new]

solutions_rad = fsolve(equations, [0.1, 0.1, 0.1])
solutions_deg = np.degrees(solutions_rad)

print("Expected Joint:", np.round(solutions_deg, 4))

joint = (f"joint: 1.19,38.80,35.02")
print(joint)

exit()


import numpy as np
from scipy.optimize import fsolve
import time
from pydobot.dobot import MODE_PTP
import pydobot

# Target values and link lengths
X_new, Y_new, Z_new = 307.61, 6.73, 31.34
a1, a2, a4, a3, b3, a5, b5 = 0, 150, 150, 25, 50, 40, 30
print(f"requested X, Y, Z:{X_new}, {Y_new}, {Z_new}")
# Define system of residual equations (Eq - Target = 0)
def equations(q):
    J1, J2, J3 = q
    Px = np.cos(J1) * (a5 + b3 + a4 * np.cos(J3) + a2 * np.sin(J2))
    Py = np.sin(J1) * (a5 + b3 + a4 * np.cos(J3) + a2 * np.sin(J2))
    Pz = a1 + a3 - b5 + a2 * np.cos(J2) - a4 * np.sin(J3) + 5

    return [Px - X_new, Py - Y_new, Pz - Z_new]

solutions_rad = fsolve(equations, [0.1, 0.1, 0.1])
solutions_deg = np.degrees(solutions_rad)

print("Expected Joint:", np.round(solutions_deg, 4))



device = pydobot.Dobot(port="COM3")
device.speed(100, 100)
device.home()
device.speed(100, 100)

def getPose(req:str="any"):
    (pose, joint) = device.get_pose()  # Get the current position and joint angles
    [x, y, z, r] = pose
    [j1, j2, j3, j4] = joint
    position = (f"pose:{x:.2f}, {y:.2f}, {z:.2f}")
    joint = (f"joint:{j1:.2f}, {j2:.2f}, {j3:.2f}")
    if req == "p" or req == "pos": print(position)
    elif req == "j" or req == "joint": print(joint)
    else: print(position, joint)

device.move_to(mode=int(MODE_PTP.MOVL_XYZ), x=X_new, y=Y_new, z=Z_new, r=0.0)
time.sleep(4)
getPose("j")

device.close()