from asyncio.windows_events import NULL
from fastapi import APIRouter, HTTPException
from typing import List
from .models import Event
from .file_storage import EventFileManager

router = APIRouter()


@router.get("/events", response_model=List[Event])
async def get_all_events():
     return EventFileManager.read_events_from_file()


@router.get("/events/filter", response_model=List[Event])
async def get_events_by_filter(date: str = None, organizer: str = None, status: str = None, event_type: str = None):
    events = EventFileManager.read_events_from_file()
    if date:
        events = [event for event in events if event['date'] == date]
    if organizer:
        events = [event for event in events if event['organizer']['email'] == organizer]
    if status:
        events = [event for event in events if event['status'] == status]
    if event_type:
        events = [event for event in events if event['type'] == event_type]     
    if not any([date, organizer, status, event_type]):
        raise HTTPException(status_code=400, detail="At least one filtering parameter required")
    else:
        raise HTTPException(status_code=400, detail="At least one filtering parameter required")

    return events


@router.get("/events/{event_id}", response_model=Event)
async def get_event_by_id(event_id: int):
    events = EventFileManager.read_events_from_file()
    for ev in events:
        if ev["id"] == event_id:
            return ev
        else:
            raise HTTPException(status_code=400, detail="Event not found")


@router.post("/events", response_model=Event)
async def create_event(event: Event):
    events = EventFileManager.read_events_from_file()
    analyzer = EventAnalyzer(events)
    event_count=analyzer.get_eventid_count()
    event_withoutid = False

    if not event.id:
        event_withoutid = True

    for existing_event in events:
        if not event_withoutid:
            if existing_event["id"] == event.id:
                raise HTTPException(status_code=400, detail="Event ID already exists")

    if event_withoutid:
        event.id = event_count + 1

    events.append(event.dict())

    EventFileManager.write_events_to_file(events)
    return event


@router.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: int, event: Event):
    events = EventFileManager.read_events_from_file()
    for event in events:
        if event["id"] == event_id:
            event.update(event.dict())
            EventFileManager.write_events_to_file(events)
            return event


@router.delete("/events/{event_id}")
async def delete_event(event_id: int):
    events = EventFileManager.read_events_from_file()
    event_f = False
    for event in events:
        if event["id"] == event_id:
                updated_events = [event for event in events if event["id"] != event_id]
                EventFileManager.write_events_to_file(updated_events)
        else:
            raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event deleted successfully"}


@router.get("/events/joiners/multiple-meetings")
async def get_joiners_multiple_meetings():
    events = EventFileManager.read_events_from_file()
    analyzer = EventAnalyzer(events)
    filtered_joiners = analyzer.get_joiners_multiple_meetings()

    if not filtered_joiners:
        return {"message": "No joiners attending at least 2 meetings"}
    else:
        return filtered_joiners


class EventAnalyzer:
    def __init__(self, events):
        self.events = events

        def get_joiners_multiple_meetings(self):
            joiners = {}
            for event in self.events:
                for joiner in event['joiners']:
                    if joiner['email'] in joiners:
                        joiners[joiner['email']]['meetings_attended'] += 1
                    else:
                        joiners[joiner['email']] = {
                            'full_name': joiner['name'],
                            'email': joiner['email'],
                            'meetings_attended': 1
                    }

        # Filter joiners who attended at least 2 meetings
            filtered_joiners = [joiner for joiner in joiners.values() if joiner['meetings_attended'] >= 2]

            return filtered_joiners
        def get_eventid_count(self):
            eventid_count = 0
            for event in self.events:
                eventid_count += 1
            return eventid_count