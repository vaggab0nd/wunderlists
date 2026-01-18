from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models.location import Location
from backend.app.schemas.location import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter(prefix="/api/locations", tags=["locations"])

@router.get("/", response_model=List[LocationResponse])
def get_locations(
    skip: int = 0,
    limit: int = 100,
    show_in_dashboard_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all locations"""
    query = db.query(Location)

    if show_in_dashboard_only:
        query = query.filter(Location.show_in_dashboard == True)

    locations = query.offset(skip).limit(limit).all()
    return locations

@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a specific location by ID"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Create a new location"""
    db_location = Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@router.put("/{location_id}", response_model=LocationResponse)
def update_location(location_id: int, location_update: LocationUpdate, db: Session = Depends(get_db)):
    """Update a location"""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")

    update_data = location_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)

    db.commit()
    db.refresh(db_location)
    return db_location

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    """Delete a location"""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(db_location)
    db.commit()
    return None
