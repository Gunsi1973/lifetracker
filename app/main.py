# app/main.py
# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles  # Missing import
from fastapi.responses import HTMLResponse    # Missing import
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging

# Internal imports
from . import models, schemas, database
from .database import engine, get_db

# Setup logging to see errors in your terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables if they do not exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LifeTracker API", version="1.0.0")
# Mount static files (for CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
# Optional: If you want to use templates
# templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return f.read()

# --- CATEGORIES ---

@app.post("/categories/", response_model=schemas.CategoryBase)
def create_category(category: schemas.CategoryBase, db: Session = Depends(get_db)):
    try:
        db_category = models.Category(**category.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- EVENTS ---

@app.post("/events/", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    try:
        # 1. Prepare base event data (excluding predecessor_ids as it's not a column)
        event_data = event.model_dump(exclude={"predecessor_ids"})
        db_event = models.Event(**event_data)
        
        # 2. Add and flush to get an ID from MariaDB
        db.add(db_event)
        db.flush() 

        # 3. Handle Dependencies (Predecessors)
        if event.predecessor_ids:
            for pred_id in event.predecessor_ids:
                predecessor = db.query(models.Event).filter(models.Event.id == pred_id).first()
                
                if not predecessor:
                    db.rollback()
                    raise HTTPException(status_code=404, detail=f"Predecessor ID {pred_id} not found")
                
                # Logical Timeline Check
                if predecessor.end_date and db_event.start_date:
                    if predecessor.end_date > db_event.start_date:
                        db.rollback()
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Timeline Conflict: Predecessor '{predecessor.title}' ends after this event starts."
                        )
                
                db_event.predecessors.append(predecessor)

        db.commit()
        db.refresh(db_event)
        return db_event

    except HTTPException as http_ex:
        # Re-raise HTTP exceptions (like our 400 or 404)
        raise http_ex
    except Exception as e:
        db.rollback()
        logger.error(f"Critical error in create_event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/", response_model=List[schemas.EventResponse])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Standard query to fetch events
    return db.query(models.Event).offset(skip).limit(limit).all()

# --- PERSONS ---

@app.post("/persons/", response_model=schemas.PersonResponse)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    try:
        db_person = models.Person(**person.model_dump())
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating person: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/persons/", response_model=List[schemas.PersonResponse])
def read_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


# --- SPECIAL VIEW ---

@app.get("/timeline/full")
def get_full_timeline(db: Session = Depends(get_db)):
    """
    Fetches the combined timeline from the MariaDB View 
    including real events and birthdays.
    """
    try:
        # Changed database.sqlalchemy.text to just text(...)
        result = db.execute(text("SELECT * FROM view_complete_timeline"))
        
        # Transform rows into a list of dictionaries for JSON response
        return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"Error fetching view: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error: {str(e)}" # Provides more detail in the API response
        )