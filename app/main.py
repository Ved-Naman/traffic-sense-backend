from fastapi import FastAPI, HTTPException, BackgroundTasks
from app.schemas import VisionMetricInput, EmergencyTrigger, SignalColor
from app.traffic_engine import calculate_traffic_score, decide_green_duration
from app.state_machine import SignalStateMachine

app = FastAPI(title="TrafficSense AI Backend", version="1.0.0")

# In-memory junction states (can be backed by Redis / PostgreSQL)
junction_states = {
    "J1": SignalStateMachine(junction_id="J1")
}

live_metrics_store = {}

@app.post("/api/vision/metrics", tags=["Vision Ingestion"])
async def ingest_vision_metrics(metrics: VisionMetricInput, background_tasks: BackgroundTasks):
    """Receives YOLO detections, computes Traffic Score, and triggers safe signal adjustment."""
    # Fail-safe check
    if not metrics.camera_healthy:
        return {"status": "FALLBACK", "message": "Camera unhealthy; falling back to static timing."}

    # Count unique vehicles from Tracking IDs
    unique_count = len(set(metrics.vehicle_ids))
    score, level = calculate_traffic_score(unique_count, metrics.lane_occupancy)
    recommended_duration = decide_green_duration(score, level)

    # Store latest state for the dashboard
    live_metrics_store[metrics.junction_id] = {
        "lane_id": metrics.lane_id,
        "unique_vehicle_count": unique_count,
        "lane_occupancy": metrics.lane_occupancy,
        "traffic_score": score,
        "traffic_level": level,
        "recommended_green_time": recommended_duration
    }

    # Trigger safe signal state machine transition asynchronously
    state_machine = junction_states.get(metrics.junction_id)
    if state_machine and not state_machine.emergency_mode:
        background_tasks.add_task(
            state_machine.transition_to_lane,
            next_lane=metrics.lane_id,
            green_duration=recommended_duration
        )

    return {
        "traffic_score": score,
        "traffic_level": level,
        "recommended_green_duration": recommended_duration
    }

@app.get("/api/dashboard/stats/{junction_id}", tags=["Traffic Police Dashboard"])
async def get_dashboard_stats(junction_id: str):
    """Provides real-time traffic statistics and signal status for the dashboard."""
    metrics = live_metrics_store.get(junction_id, {})
    state_machine = junction_states.get(junction_id)

    return {
        "junction_id": junction_id,
        "current_signal_color": state_machine.current_state if state_machine else SignalColor.ALL_RED,
        "active_lane": state_machine.active_lane if state_machine else None,
        "metrics": metrics
    }

@app.post("/api/emergency/trigger", tags=["Emergency Services"])
async def trigger_emergency(emergency: EmergencyTrigger, background_tasks: BackgroundTasks):
    """Overrides adaptive timing to establish a prioritized green corridor."""
    state_machine = junction_states.get(emergency.junction_id)
    if not state_machine:
        raise HTTPException(status_code=404, detail="Junction not found")

    state_machine.emergency_mode = True
    background_tasks.add_task(
        state_machine.transition_to_lane,
        next_lane=emergency.priority_lane,
        green_duration=90
    )
    return {"status": "EMERGENCY_ACTIVE", "priority_lane": emergency.priority_lane}