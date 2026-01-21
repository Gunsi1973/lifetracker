# app/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, Table, CheckConstraint
from sqlalchemy.orm import relationship
from .database import Base

# Association Table for Many-to-Many relationship between Events and Persons
event_participants = Table(
    "event_participants",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
    Column("participant_role", String(100))
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color_code = Column(String(7), default="#3498db")
    description = Column(String(255))

    events = relationship("Event", back_populates="category")

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)

    events = relationship("Event", secondary=event_participants, back_populates="participants")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    is_milestone = Column(Boolean, default=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="events")
    participants = relationship("Person", secondary=event_participants, back_populates="events")
    
    # Self-referencing relationship for dependencies
    predecessors = relationship(
        "Event",
        secondary="event_dependencies",
        primaryjoin="Event.id==event_dependencies.c.event_id",
        secondaryjoin="Event.id==event_dependencies.c.predecessor_id",
        backref="successors"
    )

    __table_args__ = (
        CheckConstraint("end_date IS NULL OR start_date IS NULL OR end_date >= start_date", name="chk_dates"),
    )

# Simple Table for dependencies (no extra class needed unless we add more attributes)
event_dependencies = Table(
    "event_dependencies",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("predecessor_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("dependency_type", String(50), default="requires_completion"),
    CheckConstraint("event_id <> predecessor_id", name="chk_no_self_dependency")
)