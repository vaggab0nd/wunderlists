from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models.list import List as ListModel
from backend.app.schemas.list import ListCreate, ListUpdate, ListResponse

router = APIRouter(prefix="/api/lists", tags=["lists"])

@router.get("/", response_model=List[ListResponse])
@router.get("", response_model=List[ListResponse])
def get_lists(
    skip: int = 0,
    limit: int = 100,
    include_archived: bool = False,
    db: Session = Depends(get_db)
):
    """Get all lists"""
    query = db.query(ListModel)

    if not include_archived:
        query = query.filter(ListModel.is_archived == False)

    lists = query.offset(skip).limit(limit).all()
    return lists

@router.get("/{list_id}", response_model=ListResponse)
def get_list(list_id: int, db: Session = Depends(get_db)):
    """Get a specific list by ID"""
    list_item = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    return list_item

@router.post("/", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
def create_list(list_data: ListCreate, db: Session = Depends(get_db)):
    """Create a new list"""
    db_list = ListModel(**list_data.model_dump())
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

@router.put("/{list_id}", response_model=ListResponse)
def update_list(list_id: int, list_update: ListUpdate, db: Session = Depends(get_db)):
    """Update a list"""
    db_list = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")

    update_data = list_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_list, field, value)

    db.commit()
    db.refresh(db_list)
    return db_list

@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(list_id: int, db: Session = Depends(get_db)):
    """Delete a list and all its tasks"""
    db_list = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")

    db.delete(db_list)
    db.commit()
    return None
