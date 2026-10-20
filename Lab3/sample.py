from ultralytics import YOLO

model = YOLO("yolov8s.pt")

# Validate the model
metrics = model.val()
print(f"Top-1 Accuracy: {metrics.top1:.4f}")
print(f"Top-5 Accuracy: {metrics.top5:.4f}")

# Export to ONNX format (optional)
model.export(format="onnx")
