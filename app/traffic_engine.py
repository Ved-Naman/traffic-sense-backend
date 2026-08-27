from app.schemas import TrafficLevel

MAX_CAPACITY = 50.0  # Max expected vehicles per lane to normalize count

def calculate_traffic_score(vehicle_count: int, lane_occupancy: float) -> tuple[float, TrafficLevel]:
    # Normalize vehicle count to a 0.0 - 1.0 range
    normalized_count = min(vehicle_count / MAX_CAPACITY, 1.0)

    # Official Formula
    score = round((0.6 * normalized_count) + (0.4 * lane_occupancy), 2)

    # Classify traffic condition
    if score <= 0.30:
        level = TrafficLevel.LOW
    elif score <= 0.60:
        level = TrafficLevel.MEDIUM
    elif score <= 0.80:
        level = TrafficLevel.HIGH
    else:
        level = TrafficLevel.VERY_HIGH

    return score, level

def decide_green_duration(score: float, level: TrafficLevel) -> int:
    """Recommends green light duration in seconds based on congestion."""
    duration_map = {
        TrafficLevel.LOW: 15,
        TrafficLevel.MEDIUM: 30,
        TrafficLevel.HIGH: 45,
        TrafficLevel.VERY_HIGH: 60
    }
    return duration_map[level]