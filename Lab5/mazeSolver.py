import numpy as np
import cv2  
from pydobot.dobot import MODE_PTP
import time
import pydobot
import json

with open("05_solution_path_points_unwarped.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    sol = data['unwarped_path_pixels']


def apply_affine(M, u, v):
    uv1 = np.array([u, v, 1.0], dtype=np.float64)
    XY = M @ uv1
    return float(XY[0]), float(XY[1])

M = np.array([
    [ 1.93502508e-03, -4.60556222e-01,  3.99721064e+02],
    [-4.47575572e-01, -3.50600293e-03,  1.31399179e+02],
], dtype=np.float64)

H = np.array([
    [-1.60548526e-02, -4.79420534e-01,  3.94963758e+02],
    [-4.32494808e-01, -3.51906287e-03,  1.27271081e+02],
    [-4.68500553e-05, -1.96936903e-04,  1.00000000e+00]
], dtype=np.float64)

def main():
    device = pydobot.Dobot(port="/dev/ttyACM0")
    device.speed(80, 80)
    print("Moving Device to Home")
    device.home()
    time.sleep(3)
    
    for (u, v) in sol:
        Xa, Ya = apply_affine(M, u, v) # Using Affine
        print(f"Affine:  pixel({u:.3f}, {v:.3f}) -> robot({Xa:.6f}, {Ya:.6f})")
        device.move_to(mode=int(MODE_PTP.MOVL_XYZ), x=Xa, y=Ya, z=-43, r=0.0)
        time.sleep(1)
    
    time.sleep(3)
    device.home()
    
    device.close() 
    
if __name__ == "__main__":
    main()
