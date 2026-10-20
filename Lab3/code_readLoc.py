import time
from pydobot.dobot import MODE_PTP
import pydobot

device = pydobot.Dobot(port="/dev/ttyACM0")
def getPose():
    (pose, joint) = device.get_pose()
    [x, y, z, r] = pose
    [j1, j2, j3, j4] = joint
    # position, joint = pose.position, pose.joints
    print(f"pose:{x:.2f}, {y:.2f}, {z:.2f}", )

getPose()
device.close()