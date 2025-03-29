from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5555",
    "http://194.199.113.66:31556",  # Add your frontend's origin
    "http://194.199.113.66",     # Add other allowed origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Origins allowed to make requests
    allow_credentials=True,
    allow_methods=["*"],    # HTTP methods allowed
    allow_headers=["*"],    # HTTP headers allowed
)

# In-memory storage for events
buffering_events = []
startup_times = []

class BufferingEvent(BaseModel):
    startTime: datetime
    duration: Optional[float] = None

class StartupEvent(BaseModel):
    startupDuration: float

@app.post("/buffering", status_code=201)
async def log_buffering_event(event: BufferingEvent):
    buffering_events.append(event.dict())
    print(f"Buffering Event Received: {event}")
    return {"message": "Buffering event logged successfully"}

@app.post("/startup", status_code=201)
async def log_startup_event(event: StartupEvent):
    startup_times.append(event.dict())
    print(f"Startup Event Received: {event}")
    return {"message": "Startup time logged successfully"}

@app.get("/events/buffering", response_model=List[BufferingEvent])
async def get_buffering_events():
    return buffering_events

@app.get("/events/startup", response_model=List[StartupEvent])
async def get_startup_events():
    return startup_times


