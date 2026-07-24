from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON
from .database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, unique=True, index=True, nullable=False)
    source_url = Column(String)
    title = Column(String)
    make = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer, index=True)
    price_mnt = Column(Integer)
    price_display = Column(String)
    mileage_km = Column(Integer)
    transmission = Column(String)
    engine_volume = Column(Float)
    fuel_type = Column(String)
    body_type = Column(String)
    color = Column(String)
    interior_color = Column(String)
    steering = Column(String)
    drive_type = Column(String)
    doors = Column(Integer)
    condition = Column(String)
    import_year = Column(Integer)
    leasing = Column(String)
    location = Column(String)
    image_urls = Column(JSON, default=list)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    last_seen_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
