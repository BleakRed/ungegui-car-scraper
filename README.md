# Unegui Car Scraper

Web scraper for [unegui.mn](https://www.unegui.mn/avto-mashin/-avtomashin-zarna/) car listings. Automatically collects listings, stores them in SQLite, and provides a searchable frontend with filtering. External sites can also consume the data via API.

## Features

- **Automatic Scraping** — Scrapes all car makes from unegui.mn on a schedule (default: every 6 hours)
- **Trait Scraping** — Concurrently scrapes detail pages for body type, color, steering, drive type, condition, doors, leasing
- **Database Storage** — SQLite with SQLAlchemy, auto-upsert on re-scrape
- **Sold/Removed Detection** — Marks listings as inactive when they disappear from the source
- **Similar Cars** — Finds similar cars by make, model, year ±2, price ±30%
- **Search & Filter** — Full-text search + filters on all trait fields
- **URL-based Filters** — Frontend reads/writes query params so filter links work
- **External API** — Redirect API and car export API for third-party sites
- **Docker Ready** — docker-compose setup included

## Tech Stack

| Layer     | Tech                                    |
|-----------|----------------------------------------|
| Backend   | Python 3.12, FastAPI, SQLAlchemy       |
| Database  | SQLite                                  |
| Scraper   | requests, BeautifulSoup4, ThreadPoolExecutor |
| Frontend  | React 19, Vite                         |
| Scheduler | APScheduler                             |
| Container | Docker, docker-compose                  |

## Project Structure

```
ungegui-car-scraper/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, lifespan, CORS, scheduler
│   │   ├── models.py            # SQLAlchemy Car model
│   │   ├── schemas.py           # Pydantic response schemas
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── scraper.py           # unegui.mn scraper (listings + detail pages)
│   │   ├── scheduler.py         # APScheduler background job
│   │   └── routes/
│   │       └── cars.py          # All API endpoints
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env                     # Environment config
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CarCard.jsx      # Car listing card
│   │   │   ├── CarGrid.jsx      # Grid layout for cards
│   │   │   ├── Pagination.jsx   # Page navigation
│   │   │   └── SearchFilters.jsx # All filter controls
│   │   ├── pages/
│   │   │   ├── HomePage.jsx     # Main search + listing page
│   │   │   └── CarDetailPage.jsx # Car detail + similar cars
│   │   ├── api.js               # API helper functions
│   │   ├── App.jsx              # Router setup
│   │   └── main.jsx             # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml
├── Makefile
└── README.md
```

## Setup

### Local Development

```bash
# Install all dependencies
make install

# Start backend (port 8000)
make backend

# Start frontend (port 5173) in another terminal
make frontend

# Manual scrape
make scrape
```

### Docker

```bash
make docker-up      # build + run
make docker-down    # stop
```

The backend auto-scrapes on first startup. The frontend proxies `/api` requests to the backend via Vite.

### Manual Setup

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./cars.db` | SQLite database path |
| `SCRAPE_INTERVAL_HOURS` | `6` | Hours between auto-scrapes |
| `AUTO_SCRAPE` | `true` | Run scrape on startup |
| `MAX_DETAIL_PAGES` | `20` | Max detail pages to scrape for traits per batch |
| `FRONTEND_URL` | `http://localhost:5173` | Your frontend URL (used by redirect API) |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` | Backend API URL (use `http://backend:8000/api` in Docker) |

## API Endpoints

### `GET /api/cars` — List Cars (Full)

Paginated list of active cars with full details and all filter support.

```
GET /api/cars?make=Toyota&model=Camry&year_from=2018&price_max=50000000&page=1&limit=20
```

**Response:**
```json
{
  "cars": [
    {
      "id": 1,
      "source_id": "10547605",
      "source_url": "https://www.unegui.mn/adv/10547605_toyota-camry-2018-2026/",
      "title": "Toyota Camry, 2018",
      "make": "Toyota",
      "model": "Camry",
      "year": 2018,
      "price_mnt": 35000000,
      "price_display": "35 сая₮",
      "mileage_km": 85000,
      "transmission": "Автомат",
      "engine_volume": 2.5,
      "fuel_type": "Бензин",
      "body_type": "Суудлын тэрэг",
      "color": "Цагаан",
      "steering": "Зүүн",
      "drive_type": "FWD",
      "doors": 5,
      "condition": "Дугаартай нь зарна",
      "leasing": "Лизинггүй",
      "location": "Баянгол, Улаанбаатар",
      "image_urls": ["https://cdn1.unegui.mn/media/..."],
      "description": "...",
      "is_active": true,
      "last_seen_at": "2026-07-24T05:14:27",
      "created_at": "2026-07-24T03:00:00",
      "updated_at": "2026-07-24T05:14:58"
    }
  ],
  "total": 92,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```

### `GET /api/cars/{id}` — Car Detail

Returns full details for a single car.

### `GET /api/cars/{id}/similar` — Similar Cars

Returns cars with same make/model, year ±2, price ±30%. Accepts `limit` param (default 10, max 50).

### `GET /api/cars/export` — Export Cars (Simplified)

Simplified listing for external sites. Returns only make, model, year, price, and a link.

```
GET /api/cars/export?make=TOYOTA&model=Crown&limit=10
```

**Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `make` | string | — | Filter by make (case-insensitive) |
| `model` | string | — | Filter by model (case-insensitive) |
| `year_from` | int | — | Min year |
| `year_to` | int | — | Max year |
| `price_min` | int | — | Min price (MNT) |
| `price_max` | int | — | Max price (MNT) |
| `fuel` | string | — | Fuel type filter |
| `transmission` | string | — | Transmission filter |
| `body_type` | string | — | Body type filter |
| `link_to` | string | `unegui` | `unegui` for original listing URL, `frontend` for your site |
| `page` | int | `1` | Page number |
| `limit` | int | `20` | Results per page (max 100) |

**Response:**
```json
{
  "cars": [
    {
      "make": "Toyota",
      "model": "Crown",
      "year": 2019,
      "price": "65 сая₮",
      "link": "https://www.unegui.mn/adv/10573445_toyota-crown-2019-2025/"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

Use `?link_to=frontend` to get links to your own frontend instead of unegui.

### `GET /api/redirect` — Redirect URL

Returns a prefilled frontend URL with filters. For external sites to link users to filtered results.

```
GET /api/redirect?make=Toyota&model=Camry&year_from=2018
```

**Response:**
```json
{
  "redirect_url": "http://localhost:5173/?make=Toyota&model=Camry&year_from=2018"
}
```

**Supported filters:** `make`, `model`, `year_from`, `year_to`, `price_min`, `price_max`, `fuel`, `transmission`, `body_type`, `color`, `steering`, `drive_type`, `condition`, `doors`, `leasing`, `location`

### `POST /api/scrape` — Trigger Scrape

Manually trigger a scrape. Optional `max_pages` param (1–100).

```bash
curl -X POST "http://localhost:8000/api/scrape?max_pages=5"
```

**Response:**
```json
{
  "message": "Scrape completed",
  "cars_scraped": 300,
  "new_cars": 15,
  "updated_cars": 285
}
```

### `GET /api/stats` — Scraper Statistics

```json
{
  "total_cars": 500,
  "active_cars": 480,
  "inactive_cars": 20,
  "last_scrape": "2026-07-24T05:14:27"
}
```

## Data Model

```sql
cars
├── id              INTEGER PRIMARY KEY
├── source_id       TEXT UNIQUE NOT NULL     -- unegui.mn listing ID
├── source_url      TEXT                     -- original listing URL
├── title           TEXT                     -- listing title
├── make            TEXT                     -- e.g. Toyota
├── model           TEXT                     -- e.g. Camry
├── year            INTEGER                  -- manufacture year
├── price_mnt       INTEGER                  -- price in MNT
├── price_display   TEXT                     -- e.g. "35 сая₮"
├── mileage_km      INTEGER                  -- odometer in km
├── transmission    TEXT                     -- e.g. "Автомат"
├── engine_volume   REAL                     -- liters
├── fuel_type       TEXT                     -- e.g. "Бензин"
├── body_type       TEXT                     -- scraped from detail page
├── color           TEXT                     -- scraped from detail page
├── interior_color  TEXT                     -- scraped from detail page
├── steering        TEXT                     -- e.g. "Зүүн"
├── drive_type      TEXT                     -- e.g. "FWD"
├── doors           INTEGER                  -- e.g. 5
├── condition       TEXT                     -- listing condition
├── import_year     INTEGER                  -- import year
├── leasing         TEXT                     -- leasing info
├── location        TEXT                     -- e.g. "Баянгол, Улаанбаатар"
├── image_urls      JSON                     -- array of image URLs
├── description     TEXT                     -- full description
├── is_active       BOOLEAN DEFAULT TRUE     -- false if listing removed
├── last_seen_at    DATETIME                 -- last scraped timestamp
├── created_at      DATETIME
└── updated_at      DATETIME
```

## Scraper Behavior

1. **Listing scrape** — Fetches pages from `https://www.unegui.mn/avto-mashin/-avtomashin-zarna/` (60 listings/page, all makes)
2. **Detail scrape** — Concurrently fetches up to `MAX_DETAIL_PAGES` detail pages per batch (5 workers, 10s timeout) to extract trait fields
3. **Upsert** — Existing listings are updated, new ones inserted, duplicates within a batch are deduplicated
4. **Inactive marking** — Listings not seen in the current scrape are marked `is_active=false`

## Usage by External Sites

### Option 1: Display car listings

```javascript
const res = await fetch('https://yourdomain.com/api/cars/export?make=TOYOTA&limit=10');
const data = await res.json();
data.cars.forEach(car => {
  console.log(`${car.make} ${car.model} ${car.year} — ${car.price}`);
  console.log(`Link: ${car.link}`);
});
```

### Option 2: Redirect to filtered results

```javascript
const res = await fetch('https://yourdomain.com/api/redirect?make=TOYOTA&model=Camry');
const { redirect_url } = await res.json();
window.location.href = redirect_url;
```

## License

MIT
