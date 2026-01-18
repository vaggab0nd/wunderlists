from .tasks import router as tasks_router
from .lists import router as lists_router
from .calendar_events import router as calendar_events_router
from .locations import router as locations_router

__all__ = ["tasks_router", "lists_router", "calendar_events_router", "locations_router"]
