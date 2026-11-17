import pydobot

device = pydobot.Dobot(port="/dev/ttyACM0")

#device.home()

def getPose(req:str="any"):
    (pose, joint) = device.get_pose()  # Get the current position and joint angles
    [x, y, z, r] = pose
    [j1, j2, j3, j4] = joint
    position = (f"pose:{x:.2f}, {y:.2f}, {z:.2f}")
    joint = (f"joint:{j1:.2f}, {j2:.2f}, {j3:.2f}")
    if req == "p" or req == "pos": print(position)
    elif req == "j" or req == "joint": print(joint)
    else: print(position, joint)

getPose("p")

device.close()
