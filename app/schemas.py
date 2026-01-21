# app/schemas.py
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import date

class CategoryBase(BaseModel):
    name: str
    color_code: Optional[str] = "#3498db"

class EventBase(BaseModel):
    title: str
    category_id: Optional[int] = None
    description: Optional[str] = None
    is_public: bool = False
    is_milestone: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # Custom validation for chronology
    @field_validator('end_date')
    @classmethod
    def check_chronology(cls, v, info):
        if v and info.data.get('start_date') and v < info.data.get('start_date'):
            raise ValueError('end_date cannot be earlier than start_date')
        return v

class EventCreate(EventBase):
    predecessor_ids: Optional[List[int]] = [] # IDs of events that must come before

class EventResponse(EventBase):
    id: int
    category: Optional[CategoryBase] = None # Adds the category object to the output
    model_config = ConfigDict(from_attributes=True)

class PersonBase(BaseModel):
    full_name: str
    birth_date: Optional[date] = None

class PersonCreate(PersonBase):
    pass

class PersonResponse(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
