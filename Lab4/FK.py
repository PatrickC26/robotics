import time
from pydobot.dobot import MODE_PTP
import pydobot

# FK
J1, J2, J3, J4  = 27,52,24, 0


a1 = 0
a2 = 150
a4 = 150
a3 = 25
b3 = 50
a5 = 40
b5 = 30

import sympy as sp
J1_sp = J1/180*sp.pi
J2_sp = J2/180*sp.pi
J3_sp = J3/180*sp.pi
Px = sp.cos(J1_sp) * (a5 + b3 + a4 * sp.cos(J3_sp) + a2 * sp.sin(J2_sp))
Py = sp.sin(J1_sp) * (a5 + b3 + a4 * sp.cos(J3_sp) + a2 * sp.sin(J2_sp))
Pz = a1 + a3 - b5 + a2 * sp.cos(J2_sp) - a4 * sp.sin(J3_sp) +5
print(f"expected pose:{Px:.2f}, {Py:.2f}, {Pz:.2f}")


device = pydobot.Dobot(port="COM3")
device.speed(100, 100)
device.home()

def getPose(req:str="any"):
    (pose, joint) = device.get_pose()  # Get the current position and joint angles
    [x, y, z, r] = pose
    [j1, j2, j3, j4] = joint
    position = (f"pose:{x:.2f}, {y:.2f}, {z:.2f}")
    joint = (f"joint:{j1:.2f}, {j2:.2f}, {j3:.2f}")
    if req == "p" or req == "pos": print(position)
    elif req == "j" or req == "joint": print(joint)
    else: print(position, joint)

device.move_to(mode=int(MODE_PTP.MOVJ_ANGLE), x=J1, y=J2, z=J3, r=0.0)
time.sleep(4)
getPose("p")

device.close()