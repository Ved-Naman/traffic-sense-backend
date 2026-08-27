import cv2
import requests
from ultralytics import YOLO

# 1. Load the YOLO model (downloads 'yolov8n.pt' automatically on first run)
model = YOLO("yolov8n.pt")

# 2. Open the downloaded video file
cap = cv2.VideoCapture("traffic.mp4")
API_URL = "http://localhost:8000/api/vision/metrics"

print("Starting Vision Pipeline... Press 'q' on the video window to stop.")

frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        # Loop video back to beginning for continuous demonstration
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame_count += 1

    # Process vehicle tracking (classes: 2=car, 3=motorcycle, 5=bus, 7=truck)
    results = model.track(frame, persist=True, classes=[2, 3, 5, 7], verbose=False)

    # Extract unique tracking IDs assigned by YOLO
    track_ids = []
    if results[0].boxes.id is not None:
        track_ids = results[0].boxes.id.int().cpu().tolist()

    # Calculate lane occupancy ratio (based on a 30-car capacity benchmark)
    occupancy = min(len(track_ids) / 30.0, 1.0)

    # Only send an API update every 10 frames to optimize network calls
    if frame_count % 10 == 0:
        payload = {
            "junction_id": "J1",
            "lane_id": "lane_1",
            "vehicle_ids": track_ids,
            "lane_occupancy": round(occupancy, 2),
            "camera_healthy": True
        }
        try:
            response = requests.post(API_URL, json=payload, timeout=0.5)
            data = response.json()
            print(f"[Vision] Detected: {len(track_ids)} vehicles | Score: {data.get('traffic_score')} | Level: {data.get('traffic_level')} | Green: {data.get('recommended_green_duration')}s")
        except requests.exceptions.RequestException:
            print("[Warning] Backend unreachable. Check if FastAPI is running.")

    # Display video with bounding boxes and tracking IDs
    annotated_frame = results[0].plot()
    cv2.imshow("TrafficSense AI - Live Vision Feeder", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()