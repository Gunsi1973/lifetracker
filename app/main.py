from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging

from . import models, schemas, database
from .database import engine, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LifeTracker API")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/categories/", response_model=List[schemas.CategoryResponse]) # Hier "CategoryResponse" statt "CategoryBase"
def read_categories(db: Session = Depends(get_db)):
    db.expire_all()
    return db.query(models.Category).all()

@app.get("/timeline/full")
def get_full_timeline(db: Session = Depends(get_db)):
    try:
        db.expire_all()
        result = db.execute(text("SELECT * FROM view_complete_timeline"))
        return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"Timeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    try:
        event_data = event.model_dump(exclude={"predecessor_ids"})
        db_event = models.Event(**event_data)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail="Error")