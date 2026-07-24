from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CarBase(BaseModel):
    source_id: str
    source_url: Optional[str] = None
    title: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price_mnt: Optional[int] = None
    price_display: Optional[str] = None
    mileage_km: Optional[int] = None
    transmission: Optional[str] = None
    engine_volume: Optional[float] = None
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    color: Optional[str] = None
    interior_color: Optional[str] = None
    steering: Optional[str] = None
    drive_type: Optional[str] = None
    doors: Optional[int] = None
    condition: Optional[str] = None
    import_year: Optional[int] = None
    leasing: Optional[str] = None
    location: Optional[str] = None
    image_urls: list[str] = []
    description: Optional[str] = None


class CarResponse(CarBase):
    id: int
    is_active: bool
    last_seen_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CarListResponse(BaseModel):
    cars: list[CarResponse]
    total: int
    page: int
    limit: int
    pages: int


class ScrapeResponse(BaseModel):
    message: str
    cars_scraped: int
    new_cars: int
    updated_cars: int
