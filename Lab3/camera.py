import cv2
import time
from pathlib import Path
from ultralytics import YOLO

# ----------------- Configuration -----------------
# Model path: you can use your custom trained model (e.g., 'best.pt'), 
# a classification model (e.g., 'yolov8n-cls.pt'), or a detection model (e.g., 'yolov8s.pt')
MODEL_PATH = "yolov8s.pt"  
CAMERA_INDEX = 0           # 0 is usually the default built-in webcam
CONFIDENCE_THRESHOLD = 0.25 # Minimum confidence threshold
OUTPUT_DIR = Path("cv2_capturetured_images")

# req: #1 bicycle, #2 car, #46 banana, #4 airplane, #47 apple, #53 pizza, 
RIGHT_PALLET = [1, 2, 4, 36]
LEFT_PALLET = [46, 47, 53]

isRobotClassifying = False
isRobotLastRun = False
# -------------------------------------------------
cv2_capture = None
model = None


def main():
    prev_time = time.time()
    global cv2_capture, model, isRobotClassifying, isRobotLastRun
    if cv2_capture is None or model is None: yoloInit()

    while True:
        ret, frame = cv2_capture.read()
        if not ret: break
        if isRobotLastRun: 
            isRobotLastRun = False
            continue

        # Run YOLO inference on the current frame
        results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        result = results[0]

        # get objects 
        objects = result.boxes.cls
        # names: {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}
        # req: #1 bicycle, #2 car, #46 banana, #4 airplane, #47 apple, #53 pizza, 

        ## deal with specific items 
        req_items = [1, 2, 46, 36, 4, 47, 53]
        for i, obj in enumerate(objects):
            if int(obj.item()) in req_items:
                print(result.names[int(obj.item())])

                # get box area 
                x_min, y_min, x_max, y_max = result.boxes.xyxy[i]
                x_mid, y_mid = (x_min + x_max)/2, (y_min + y_max)/2
                print(x_mid, y_mid)
                # (320, 100) should be within the area
                if 260 < x_mid < 300 and 100 < y_mid < 130:
                    if not isRobotClassifying: 
                        graspNclassfiy(int(obj.item()))
                        break

        # Automatically annotates frame with boxes/labels (works for detection and classification)
        annotated_frame = result.plot()

        # Calculate and display FPS
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.1f} | Task: {model.task}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        # rec box
        start_point = (260, 100)  # (X_min, Y_min)
        end_point = (300, 130)    # (X_max, Y_max)
        color = (0, 255, 0)
        thickness = 2
        annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color, thickness)
        

        # Show the annotated frame
        cv2.imshow("YOLO Camera Feed", annotated_frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key in [ord("q"), 27]:  # 'q' or ESC
            print("Exiting...")
            break
        elif key == ord("s"):      # 's' to save
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            raw_path = OUTPUT_DIR / f"raw_{timestamp}.jpg"
            annotated_path = OUTPUT_DIR / f"annotated_{timestamp}.jpg"
            
            cv2.imwrite(str(raw_path), frame)
            cv2.imwrite(str(annotated_path), annotated_frame)
            print(f"Saved: {raw_path} and {annotated_path}")

        elif key == 32:            # Spacebar to print details
            print(f"\n--- Frame Analysis ({model.task}) ---")
            if result.probs is not None:
                # Classification model
                top1_idx = result.probs.top1
                top1_name = result.names[top1_idx]
                top1_conf = result.probs.top1conf.item()
                print(f"Top-1: {top1_name} ({top1_conf:.2%})")
                print("Top-5:")
                for idx in result.probs.top5:
                    print(f"  - {result.names[idx]}: {result.probs.data[idx].item():.2%}")
            elif result.boxes is not None:
                # Detection model
                print(f"Detected {len(result.boxes)} objects:")
                for box in result.boxes:
                    cls_id = int(box.cls[0].item())
                    conf = box.conf[0].item()
                    name = result.names[cls_id]
                    print(f"  - {name}: {conf:.2%}")

    # Release resources
    cv2_capture.release()
    cv2.destroyAllWindows()


device = None
def dobotInit():
    global device
    from pydobot.dobot import MODE_PTP
    import pydobot
    device = pydobot.Dobot(port="/dev/ttyACM0")
    device.home()

def getPose():
    (pose, joint) = device.get_pose()
    [x, y, z, r] = pose
    [j1, j2, j3, j4] = joint
    # position, joint = pose.position, pose.joints
    print(f"pose:{x:.2f}, {y:.2f}, {z:.2f}", )


def graspNclassfiy(cls_id):
    from pydobot.dobot import MODE_PTP
    global device, isRobotClassifying, cv2_capture, isRobotLastRun
    if isRobotClassifying: return
    
    isRobotClassifying = True
    isRobotLastRun = True
    print("Robot Doing Classifying")
    # req: #1 bicycle, #2 car, #46 banana, #4 airplane, #47 apple, #53 pizza, 
    # mid point of item 276.23, 56.53, -54.39
    # device.home()  # Home the robot to the origin position
    print(cls_id) 
    # move to init 
    device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=340, y=4, z=-55.5, r=0.0)
    time.sleep(1.5)
    device.suck(True)
    time.sleep(1)
    device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=340, y=4, z=-30, r=0.0)
    time.sleep(0.5)
    
    if cls_id in RIGHT_PALLET: 
        print("TO right pallet")
        device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=300, y=100, z=-40, r=0.0) 
    elif cls_id in LEFT_PALLET:  
        print("TO left pallet")
        device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=300, y=-100, z=-40, r=0.0) 
    else: 
        print("TO middle bin")
        device.move_to(mode=int(MODE_PTP.MOVJ_XYZ), x=230, y=0, z=-40, r=0.0)
    time.sleep(1)

    device.suck(False)
    time.sleep(.5)
    device.home()
    time.sleep(2)
    
    isRobotClassifying = False
    # cv2_capture.()
    print("Robot Done Classifying")


def yoloInit():
    global cv2_capture, model
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading YOLO model from: {MODEL_PATH} ...")
    model = YOLO(MODEL_PATH)

    # Initialize webcam
    cv2_capture = cv2.VideoCapture(CAMERA_INDEX)
    cv2_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
    if not cv2_capture.isOpened():
        print(f"Error: Could not open camera at index {CAMERA_INDEX}.")
        return

    # Set camera resolution (optional, e.g., 640x480 or 1280x720)
    cv2_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cv2_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("\nControls:")
    print("  [q] or [ESC] : Quit")
    print("  [s]         : Save current frame to disk")
    print("  [Space]     : Run/Print detailed prediction to console\n")

    


if __name__ == "__main__":
    yoloInit()
    dobotInit()
    main()

    device.close()
