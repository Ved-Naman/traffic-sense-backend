from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SignalColor(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ALL_RED = "ALL_RED"

class TrafficLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class VisionMetricInput(BaseModel):
    junction_id: str
    lane_id: str
    vehicle_ids: List[int] = Field(..., description="Unique Tracking IDs across frames")
    lane_occupancy: float = Field(..., ge=0.0, le=1.0, description="0.0 to 1.0 occupancy ratio")
    camera_healthy: bool = True

class EmergencyTrigger(BaseModel):
    junction_id: str
    priority_lane: str
    vehicle_type: str = "AMBULANCE"  # AMBULANCE / FIRE_SERVICE
    authorized_token: str