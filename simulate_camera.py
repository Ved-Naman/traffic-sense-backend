import requests
import time
import random

# The URL of your local FastAPI backend
API_URL = "http://localhost:8000/api/vision/metrics"

def simulate_traffic():
    print("Starting Vision Feed Simulator... Press Ctrl+C to stop.")

    while True:
        # Simulate dynamic traffic conditions
        # Generating random vehicle IDs to simulate busy or light traffic
        num_vehicles = random.randint(5, 45)
        vehicle_ids = list(range(1, num_vehicles + 1))

        # Simulate lane occupancy between 10% (0.1) and 90% (0.9)
        occupancy = round(random.uniform(0.1, 0.9), 2)

        # The payload matches our VisionMetricInput schema
        payload = {
            "junction_id": "J1",
            "lane_id": "lane_1",
            "vehicle_ids": vehicle_ids,
            "lane_occupancy": occupancy,
            "camera_healthy": True
        }

        try:
            # Send the data to the backend
            response = requests.post(API_URL, json=payload)
            data = response.json()

            print(f"Sent: {num_vehicles} vehicles | Occupancy: {occupancy}")
            print(f"Backend Response -> Score: {data.get('traffic_score')} | Level: {data.get('traffic_level')} | Green Time: {data.get('recommended_green_duration')}s")
            print("-" * 50)

        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to the backend. Is FastAPI running?")

        # Wait a few seconds before sending the next frame of data
        time.sleep(5)

if __name__ == "__main__":
    simulate_traffic()