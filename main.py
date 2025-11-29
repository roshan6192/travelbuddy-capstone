from fastapi import FastAPI
from pydantic import BaseModel
from coordinator import TravelBuddyCoordinator

app = FastAPI()

class TripRequest(BaseModel):
    user_id: str = "default_user"
    request: str
    budget: float = 1000.0


@app.post("/plan_trip")
def plan_trip(body: TripRequest):
    coordinator = TravelBuddyCoordinator(user_id=body.user_id)
    result = coordinator.handle_request(body.request, body.budget)
    return result