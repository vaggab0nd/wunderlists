"""
Admin endpoints for database maintenance and cleanup.

WARNING: These endpoints are destructive and should be used with caution.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.database import get_db
from backend.app.models.task import Task
from backend.app.models.list import List
from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.location import Location

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.delete("/clear-all-data")
def clear_all_data(
    confirm: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Clear ALL data from the database (tasks, lists, calendar events, locations).

    WARNING: This is irreversible! All your data will be permanently deleted.

    To confirm, pass confirm="YES_DELETE_EVERYTHING" as a query parameter:
    DELETE /api/admin/clear-all-data?confirm=YES_DELETE_EVERYTHING

    Returns:
        Summary of deleted records
    """
    if confirm != "YES_DELETE_EVERYTHING":
        raise HTTPException(
            status_code=400,
            detail="To confirm deletion, add query parameter: ?confirm=YES_DELETE_EVERYTHING"
        )

    try:
        # Count before deletion
        tasks_count = db.query(Task).count()
        lists_count = db.query(List).count()
        events_count = db.query(CalendarEvent).count()
        locations_count = db.query(Location).count()

        # Delete all records (order matters due to foreign keys)
        db.query(Task).delete()
        db.query(CalendarEvent).delete()
        db.query(Location).delete()
        db.query(List).delete()

        db.commit()

        return {
            "status": "success",
            "message": "All data has been cleared",
            "deleted": {
                "tasks": tasks_count,
                "lists": lists_count,
                "calendar_events": events_count,
                "locations": locations_count,
                "total": tasks_count + lists_count + events_count + locations_count
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear data: {str(e)}"
        )


@router.get("/stats")
def get_database_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get current database statistics (record counts).

    Returns:
        Counts of all records in the database
    """
    try:
        return {
            "tasks": {
                "total": db.query(Task).count(),
                "completed": db.query(Task).filter(Task.is_completed == True).count(),
                "incomplete": db.query(Task).filter(Task.is_completed == False).count()
            },
            "lists": db.query(List).count(),
            "calendar_events": db.query(CalendarEvent).count(),
            "locations": db.query(Location).count()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )
