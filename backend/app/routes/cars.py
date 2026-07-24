import math
import os
import logging
import threading
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Car
from ..schemas import CarResponse, CarListResponse, ScrapeResponse
from ..scraper import run_scraper

logger = logging.getLogger(__name__)
router = APIRouter()

_scrape_lock = threading.Lock()


@router.get("/api/cars", response_model=CarListResponse)
def list_cars(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    make: Optional[str] = None,
    model: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    fuel: Optional[str] = None,
    transmission: Optional[str] = None,
    body_type: Optional[str] = None,
    color: Optional[str] = None,
    steering: Optional[str] = None,
    drive_type: Optional[str] = None,
    condition: Optional[str] = None,
    doors: Optional[int] = None,
    leasing: Optional[str] = None,
    location: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Car).filter(Car.is_active == True)

    if make:
        query = query.filter(Car.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Car.model.ilike(f"%{model}%"))
    if year_from:
        query = query.filter(Car.year >= year_from)
    if year_to:
        query = query.filter(Car.year <= year_to)
    if price_min:
        query = query.filter(Car.price_mnt >= price_min)
    if price_max:
        query = query.filter(Car.price_mnt <= price_max)
    if fuel:
        query = query.filter(Car.fuel_type.ilike(f"%{fuel}%"))
    if transmission:
        query = query.filter(Car.transmission.ilike(f"%{transmission}%"))
    if body_type:
        query = query.filter(Car.body_type.ilike(f"%{body_type}%"))
    if color:
        query = query.filter(Car.color.ilike(f"%{color}%"))
    if steering:
        query = query.filter(Car.steering.ilike(f"%{steering}%"))
    if drive_type:
        query = query.filter(Car.drive_type.ilike(f"%{drive_type}%"))
    if condition:
        query = query.filter(Car.condition.ilike(f"%{condition}%"))
    if doors:
        query = query.filter(Car.doors == doors)
    if leasing:
        query = query.filter(Car.leasing.ilike(f"%{leasing}%"))
    if location:
        query = query.filter(Car.location.ilike(f"%{location}%"))
    if q:
        query = query.filter(
            Car.title.ilike(f"%{q}%") | Car.description.ilike(f"%{q}%")
        )

    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit
    cars = query.order_by(Car.created_at.desc()).offset(offset).limit(limit).all()

    return CarListResponse(
        cars=[CarResponse.model_validate(c) for c in cars],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/api/cars/export")
def export_cars(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    make: Optional[str] = None,
    model: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    fuel: Optional[str] = None,
    transmission: Optional[str] = None,
    body_type: Optional[str] = None,
    link_to: str = Query("unegui", description="'unegui' or 'frontend'"),
    db: Session = Depends(get_db),
):
    """
    External API for friend's site: returns a simplified list of cars
    with make, model, price, and a link.
    """
    query = db.query(Car).filter(Car.is_active == True)

    if make:
        query = query.filter(Car.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Car.model.ilike(f"%{model}%"))
    if year_from:
        query = query.filter(Car.year >= year_from)
    if year_to:
        query = query.filter(Car.year <= year_to)
    if price_min:
        query = query.filter(Car.price_mnt >= price_min)
    if price_max:
        query = query.filter(Car.price_mnt <= price_max)
    if fuel:
        query = query.filter(Car.fuel_type.ilike(f"%{fuel}%"))
    if transmission:
        query = query.filter(Car.transmission.ilike(f"%{transmission}%"))
    if body_type:
        query = query.filter(Car.body_type.ilike(f"%{body_type}%"))

    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit
    cars = query.order_by(Car.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for c in cars:
        if link_to == "frontend":
            link = f"{FRONTEND_URL}/car/{c.id}"
        else:
            link = c.source_url or ""

        results.append({
            "make": c.make,
            "model": c.model,
            "year": c.year,
            "price": c.price_display or (f"{c.price_mnt:,} ₮" if c.price_mnt else None),
            "link": link,
        })

    return {
        "cars": results,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


@router.get("/api/cars/{car_id}", response_model=CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return CarResponse.model_validate(car)


@router.get("/api/cars/{car_id}/similar", response_model=CarListResponse)
def get_similar_cars(
    car_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    query = db.query(Car).filter(
        Car.id != car.id,
        Car.is_active == True,
        Car.make == car.make,
        Car.model == car.model,
    )
    if car.year:
        query = query.filter(Car.year >= car.year - 2, Car.year <= car.year + 2)
    if car.price_mnt:
        low = int(car.price_mnt * 0.7)
        high = int(car.price_mnt * 1.3)
        query = query.filter(Car.price_mnt >= low, Car.price_mnt <= high)

    similar = query.limit(limit).all()
    return CarListResponse(
        cars=[CarResponse.model_validate(c) for c in similar],
        total=len(similar),
        page=1,
        limit=limit,
        pages=1,
    )


@router.post("/api/scrape", response_model=ScrapeResponse)
def trigger_scrape(max_pages: Optional[int] = Query(None, ge=1, le=100)):
    if not _scrape_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Scrape already in progress")
    try:
        stats = run_scraper(max_pages=max_pages)
        return ScrapeResponse(
            message="Scrape completed",
            cars_scraped=stats["total"],
            new_cars=stats["new"],
            updated_cars=stats["updated"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrape failed: {str(e)}")
    finally:
        _scrape_lock.release()


@router.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Car).count()
    active = db.query(Car).filter(Car.is_active == True).count()
    last_car = db.query(Car).order_by(Car.last_seen_at.desc()).first()
    return {
        "total_cars": total,
        "active_cars": active,
        "inactive_cars": total - active,
        "last_scrape": last_car.last_seen_at.isoformat() if last_car else None,
    }


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def _build_query_string(
    make, model, year_from, year_to, price_min, price_max,
    fuel, transmission, body_type, color, steering,
    drive_type, condition, doors, leasing, location,
):
    params = []
    if make: params.append(f"make={make}")
    if model: params.append(f"model={model}")
    if year_from: params.append(f"year_from={year_from}")
    if year_to: params.append(f"year_to={year_to}")
    if price_min: params.append(f"price_min={price_min}")
    if price_max: params.append(f"price_max={price_max}")
    if fuel: params.append(f"fuel={fuel}")
    if transmission: params.append(f"transmission={transmission}")
    if body_type: params.append(f"body_type={body_type}")
    if color: params.append(f"color={color}")
    if steering: params.append(f"steering={steering}")
    if drive_type: params.append(f"drive_type={drive_type}")
    if condition: params.append(f"condition={condition}")
    if doors: params.append(f"doors={doors}")
    if leasing: params.append(f"leasing={leasing}")
    if location: params.append(f"location={location}")
    return "&".join(params)


@router.get("/api/redirect")
def get_redirect_link(
    make: Optional[str] = Query(None, description="Car make, e.g. Toyota"),
    model: Optional[str] = Query(None, description="Car model, e.g. Camry"),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    price_min: Optional[int] = Query(None),
    price_max: Optional[int] = Query(None),
    fuel: Optional[str] = Query(None),
    transmission: Optional[str] = Query(None),
    body_type: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    steering: Optional[str] = Query(None),
    drive_type: Optional[str] = Query(None),
    condition: Optional[str] = Query(None),
    doors: Optional[int] = Query(None),
    leasing: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
):
    """
    External API: another site calls this with make/model (or any filters)
    and gets back a prefilled frontend URL they can send users to.
    """
    query_string = _build_query_string(
        make, model, year_from, year_to, price_min, price_max,
        fuel, transmission, body_type, color, steering,
        drive_type, condition, doors, leasing, location,
    )

    if query_string:
        redirect = f"{FRONTEND_URL}/?{query_string}"
    else:
        redirect = FRONTEND_URL

    return {"redirect_url": redirect}
