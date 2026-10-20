import time
from pydobot.dobot import MODE_PTP
import pydobot

device = pydobot.Dobot(port="/dev/ttyACM0")
device.home()  # Home the robot to the origin position
def getPose():
    (pose, joint) = device.get_pose()
    [x, y, z, r] = pose
    [j1, j2, j3, j4] = joint
    # position, joint = pose.position, pose.joints
    print(f"pose:{x:.2f}, {y:.2f}, {z:.2f}", )
device.speed(60, 100)

# def graspAndPut(x:float, y:float, dir:int=0):
#     # dir 0 is left to right, dir 1 is right to left
#     z = 17
#     device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=x, y=y, z=z, r=0.0)  # Move to position (x=250, y=0, z=50) with r=0
#     time.sleep(1)
#     z -= 60
#     device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=x, y=y, z=z, r=0.0)
#     device.suck(True)  # Turn on the suction cup
#     time.sleep(1)
#     z += 60
#     device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=x, y=y, z=z, r=0.0)
#     time.sleep(1)
#     if dir == 0: y += 200
#     else: y -= 200
#     device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=x, y=y, z=z, r=0.0)
#     time.sleep(1)
#     z -= 60
#     device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=x, y=y, z=z, r=0.0)
#     time.sleep(1)
#     device.suck(False)
#     time.sleep(2)
#     z += 60
#     device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=x, y=y, z=z, r=0.0)  # Move to position (x=250, y=0, z=50) with r=0

# # move from left to right
# graspAndPut(x=273, y=-70.0)
# graspAndPut(x=273, y=-130.0)
# graspAndPut(x=333, y=-70.0)
# graspAndPut(x=333, y=-130.0)

# # move from right to left
# graspAndPut(x=273, y=130.0, dir=1)
# graspAndPut(x=273, y=70.0, dir=1)
# graspAndPut(x=333, y=130.0, dir=1)
# graspAndPut(x=333, y=70.0, dir=1)
device.suck(True)
device.home()
device.close()