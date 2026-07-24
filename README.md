# Unegui Car Scraper

Web scraper for [unegui.mn](https://www.unegui.mn/avto-mashin/-avtomashin-zarna/toyota/) that automatically collects car listings, stores them in a database, and provides a searchable frontend with filtering.

## Features

- **Automatic Scraping** — Periodically scrapes car listings from unegui.mn (Toyota, and other brands via URL config)
- **Database Storage** — Saves car info (make, model, year, price, mileage, fuel type, transmission, location, images, etc.)
- **REST API** — FastAPI backend for reading/writing car data
- **Search & Filter** — Frontend mirrors unegui.mn's search/filter (make, model, year range, price range, mileage, fuel, transmission)
- **Sold/Removed Detection** — Marks listings as unavailable when they disappear from the source
- **Similar Cars** — Backend calculates similar cars by make, model, year, and price range

## Tech Stack

| Layer     | Tech         |
|-----------|-------------|
| Backend   | Python, FastAPI, SQLAlchemy |
| Database  | PostgreSQL (or SQLite for dev) |
| Scraper   | requests, BeautifulSoup |
| Frontend  | React (or Next.js) |
| Scheduler | APScheduler / cron |

## Project Structure

```
ungegui-car-scraper/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entrypoint
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── database.py       # DB connection
│   │   ├── scraper.py        # unegui.mn scraper logic
│   │   ├── scheduler.py      # Auto-scrape scheduler
│   │   └── routes/
│   │       ├── cars.py       # Car CRUD endpoints
│   │       └── search.py     # Search/filter endpoints
│   ├── requirements.txt
│   └── alembic/              # DB migrations
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CarList.jsx
│   │   │   ├── CarCard.jsx
│   │   │   ├── SearchFilters.jsx
│   │   │   └── CarDetail.jsx
│   │   ├── pages/
│   │   └── api/
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint              | Description               |
|--------|----------------------|---------------------------|
| GET    | `/api/cars`          | List all cars (paginated) |
| GET    | `/api/cars/{id}`     | Car detail                |
| GET    | `/api/search`        | Search/filter cars        |
| GET    | `/api/cars/similar/{id}` | Similar cars         |
| POST   | `/api/scrape`        | Trigger manual scrape     |

### Query Parameters for Search

| Param        | Type   | Example              |
|-------------|--------|----------------------|
| `make`      | string | `Toyota`             |
| `model`     | string | `Camry`              |
| `year_from` | int    | `2015`               |
| `year_to`   | int    | `2024`               |
| `price_min` | int    | `5000000`            |
| `price_max` | int    | `50000000`           |
| `fuel`      | string | `Benzin`             |
| `transmission` | string | `Automat`         |
| `page`      | int    | `1`                  |
| `limit`     | int    | `20`                 |

## Data Model

```python
class Car:
    id: int
    source_url: str          # original unegui.mn link
    title: str
    make: str                # e.g. Toyota
    model: str               # e.g. Camry
    year: int
    price: int               # in MNT
    mileage: int             # in km
    fuel_type: str
    transmission: str
    engine_volume: float     # in liters
    body_type: str
    color: str
    location: str
    image_urls: list[str]
    description: str
    seller_name: str
    seller_phone: str
    is_active: bool          # False if listing removed
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime
```

## Scraping Schedule

The backend runs the scraper every 6 hours by default. Configure via `SCRAPE_INTERVAL_HOURS` env var. A manual scrape can also be triggered via `POST /api/scrape`.
