from fastapi import APIRouter, HTTPException
from typing import List
import random
from .models import Event
from .event_analyzer import EventAnalyzer
from .file_storage import EventFileManager

router = APIRouter()

file_manager = EventFileManager()

@router.get("/events", response_model=List[Event])
async def get_all_events():
    return file_manager.read_events_from_file()


@router.get("/events/filter", response_model=List[Event])
async def get_events_by_filter(date: str = None, organizer: str = None, status: str = None, event_type: str = None):
    filtered_events = file_manager.read_events_from_file()

    if date:
        filtered_events = [event for event in filtered_events if event['date'] == date]
    if organizer:
        filtered_events = [event for event in filtered_events if event['organizer']['email'] == organizer]
    if status:
        filtered_events = [event for event in filtered_events if event['status'] == status]
    if event_type:
        filtered_events = [event for event in filtered_events if event['type'] == event_type]

    if not any([date, organizer, status, event_type]):
        raise HTTPException(status_code=400, detail="At least one filtering parameter required")

    return filtered_events




@router.get("/events/{event_id}", response_model=Event)
async def get_event_by_id(event_id: int):
    events = file_manager.read_events_from_file()
    for event in events:
        if event['id'] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")


@router.post("/events", response_model=Event)
async def create_event(event: Event):
    events = file_manager.read_events_from_file()
    
    if not event.id:
        raise HTTPException(status_code=400, detail="Event ID cannot be empty")

    for existing_event in events:
        if existing_event["id"] == event.id:
            raise HTTPException(status_code=400, detail="Event ID already exists")

    events.append(event.dict())  # Convert Event object to dictionary before appending

    file_manager.write_events_to_file(events)
    return event

@router.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: int, event: Event):
    events = file_manager.read_events_from_file()
    for i, existing_event in enumerate(events):
        if existing_event["id"] == event_id:
            events[i] = event.model_dump()
            file_manager.write_events_to_file(events)
            return event
    raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/events/{event_id}")
async def delete_event(event_id: int):
    events = file_manager.read_events_from_file()

    event_found = False
    for event in events:
        if event["id"] == event_id:
            event_found = True
            break

    if not event_found:
        raise HTTPException(status_code=404, detail="Event not found")

    updated_events = [event for event in events if event["id"] != event_id]

    file_manager.write_events_to_file(updated_events)

    return {"message": "Event deleted successfully"}


@router.get("/events/joiners/multiple-meetings")
async def get_joiners_multiple_meetings():
    events = file_manager.read_events_from_file()
    event_analyzer = EventAnalyzer(events)
    filtered_joiners = event_analyzer.get_joiners_multiple_meetings()

    if not filtered_joiners:
        return {"message": "No joiners attending at least 2 meetings"}

    random_joiner = random.choice(filtered_joiners)
    return random_joiner
