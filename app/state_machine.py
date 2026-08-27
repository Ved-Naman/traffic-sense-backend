import asyncio
from app.schemas import SignalColor

class SignalStateMachine:
    def __init__(self, junction_id: str):
        self.junction_id = junction_id
        self.active_lane = "lane_1"
        self.current_state = SignalColor.ALL_RED
        self.yellow_time = 3    # seconds
        self.all_red_time = 2   # clearance time in seconds
        self.emergency_mode = False

    async def transition_to_lane(self, next_lane: str, green_duration: int):
        """Safely cycles through Yellow -> All Red before setting the next lane Green."""
        if self.current_state == SignalColor.GREEN and self.active_lane != next_lane:
            # Step 1: Yellow Clearance
            self.current_state = SignalColor.YELLOW
            print(f"[{self.junction_id}] State -> YELLOW for {self.active_lane}")
            await asyncio.sleep(self.yellow_time)

            # Step 2: All Red Safety Clearance
            self.current_state = SignalColor.ALL_RED
            print(f"[{self.junction_id}] State -> ALL_RED (Clearance interval)")
            await asyncio.sleep(self.all_red_time)

        # Step 3: Grant Green to the target lane
        self.active_lane = next_lane
        self.current_state = SignalColor.GREEN
        print(f"[{self.junction_id}] State -> GREEN for {self.active_lane} for {green_duration}s")