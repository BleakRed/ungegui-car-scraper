import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Car

logger = logging.getLogger(__name__)

BASE_URL = "https://www.unegui.mn"
LISTING_URL = BASE_URL + "/avto-mashin/-avtomashin-zarna/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "mn-MN,mn;q=0.9,en;q=0.8",
}

TRAIT_MAP = {
    "Мотор багтаамж": "engine_volume",
    "Хурдны хайрцаг": "transmission",
    "Хүрд": "steering",
    "Төрөл": "body_type",
    "Өнгө": "color",
    "Дотор өнгө": "interior_color",
    "Үйлдвэрлэсэн он": "year",
    "Орж ирсэн он": "import_year",
    "Хөдөлгүүр": "fuel_type",
    "Лизинг": "leasing",
    "Хөтлөгч": "drive_type",
    "Явсан": "mileage_km",
    "Нөхцөл": "condition",
    "Хаалга": "doors",
}


def parse_price(price_text: str) -> Optional[int]:
    """Parse price text like '39.8 сая ₮' to integer MNT."""
    if not price_text:
        return None
    price_text = price_text.strip().replace("\xa0", " ").replace("₮", "").strip()
    try:
        multiplier = 1
        if "тэрбум" in price_text:
            multiplier = 1_000_000_000
            price_text = price_text.replace("тэрбум", "").strip()
        elif "сая" in price_text:
            multiplier = 1_000_000
            price_text = price_text.replace("сая", "").strip()
        elif "мянган" in price_text or "мян" in price_text:
            multiplier = 1_000
            price_text = price_text.replace("мянган", "").replace("мян", "").strip()
        price_text = price_text.replace(",", "").replace(" ", "")
        value = float(price_text)
        return int(value * multiplier)
    except (ValueError, TypeError):
        return None


def parse_mileage(text: str) -> Optional[int]:
    """Parse mileage text like '157000 км' to integer."""
    if not text:
        return None
    match = re.search(r"([\d\s]+)\s*км", text)
    if match:
        return int(match.group(1).replace(" ", "").replace("\xa0", ""))
    return None


def parse_engine_volume(text: str) -> Optional[float]:
    """Parse engine volume like '1.8 л' to float."""
    if not text:
        return None
    match = re.search(r"([\d.]+)\s*л", text)
    if match:
        return float(match.group(1))
    return None


def parse_title(title: str) -> tuple[Optional[str], Optional[str], Optional[int]]:
    """Parse title like 'Toyota Prius 41, 2019/2026' to (make, model, year)."""
    if not title:
        return None, None, None
    title = title.strip()
    year = None
    year_match = re.search(r",?\s*(\d{4})[/\-](\d{4})", title)
    if year_match:
        year = int(year_match.group(1))
        title = title[: year_match.start()].strip().rstrip(",")

    parts = title.split(None, 1)
    make = parts[0] if parts else None
    model = parts[1] if len(parts) > 1 else None
    return make, model, year


def parse_doors(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None


def parse_import_year(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(\d{4})", text)
    return int(match.group(1)) if match else None


def scrape_page(page: int = 1) -> tuple[list[dict], int]:
    """Scrape a single page of listings. Returns (listings, total_pages)."""
    url = LISTING_URL if page == 1 else f"{LISTING_URL}?page={page}"
    logger.info(f"Scraping page {page}: {url}")

    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    total_pages = 1
    last_link = soup.select_one('link[rel="last"]')
    if last_link:
        href = last_link.get("href", "")
        page_match = re.search(r"page=(\d+)", href)
        if page_match:
            total_pages = int(page_match.group(1))

    listings = []
    adverts = soup.select("div.advert.js-item-listing")
    for advert in adverts:
        source_id = advert.get("data-id", "")
        if not source_id:
            continue

        listing = {"source_id": source_id}

        title_el = advert.select_one("a.advert__content-title")
        if title_el:
            listing["title"] = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            if href:
                listing["source_url"] = (
                    BASE_URL + href if href.startswith("/") else href
                )

        price_el = advert.select_one("a.advert__content-price span")
        if price_el:
            listing["price_display"] = price_el.get_text(strip=True)
            listing["price_mnt"] = parse_price(listing["price_display"])

        make, model, year = parse_title(listing.get("title", ""))
        listing["make"] = make
        listing["model"] = model
        listing["year"] = year

        features = advert.select("div.advert__content-feature div")
        feature_texts = [f.get_text(strip=True) for f in features]
        if len(feature_texts) >= 1:
            listing["mileage_km"] = parse_mileage(feature_texts[0])
        if len(feature_texts) >= 2:
            listing["transmission"] = feature_texts[1]
        if len(feature_texts) >= 3:
            listing["engine_volume"] = parse_engine_volume(feature_texts[2])
        if len(feature_texts) >= 4:
            listing["fuel_type"] = feature_texts[3]

        location_el = advert.select_one("div.advert__content-place")
        if location_el:
            listing["location"] = location_el.get_text(strip=True)

        images = []
        for slide in advert.select("a.swiper-slide"):
            bg = slide.get("data-background", "")
            if bg:
                images.append(bg)
            else:
                img_tag = slide.select_one("img")
                if img_tag and img_tag.get("src"):
                    images.append(img_tag["src"])
        listing["image_urls"] = images

        listings.append(listing)

    return listings, total_pages


def scrape_traits_from_detail(url: str) -> dict:
    """Scrape trait fields from a car detail page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        traits = {}
        for li in soup.select("li"):
            key_el = li.select_one("span.key-chars")
            val_el = li.select_one("span.value-chars, a.value-chars")
            if key_el and val_el:
                key = key_el.get_text(strip=True).rstrip(":")
                val = val_el.get_text(strip=True)
                field = TRAIT_MAP.get(key)
                if field:
                    traits[field] = val

        parsed = {}
        if "engine_volume" in traits:
            parsed["engine_volume"] = parse_engine_volume(traits["engine_volume"])
        if "transmission" in traits:
            parsed["transmission"] = traits["transmission"]
        if "steering" in traits:
            parsed["steering"] = traits["steering"]
        if "body_type" in traits:
            parsed["body_type"] = traits["body_type"]
        if "color" in traits:
            parsed["color"] = traits["color"]
        if "interior_color" in traits:
            parsed["interior_color"] = traits["interior_color"]
        if "fuel_type" in traits:
            parsed["fuel_type"] = traits["fuel_type"]
        if "leasing" in traits:
            parsed["leasing"] = traits["leasing"]
        if "drive_type" in traits:
            parsed["drive_type"] = traits["drive_type"]
        if "mileage_km" in traits:
            parsed["mileage_km"] = parse_mileage(traits["mileage_km"])
        if "condition" in traits:
            parsed["condition"] = traits["condition"]
        if "doors" in traits:
            parsed["doors"] = parse_doors(traits["doors"])
        if "import_year" in traits:
            parsed["import_year"] = parse_import_year(traits["import_year"])
        if "year" in traits:
            match = re.search(r"(\d{4})", traits["year"])
            if match:
                parsed["year"] = int(match.group(1))

        return parsed
    except Exception as e:
        logger.debug(f"Error scraping traits from {url}: {e}")
        return {}


def upsert_cars(db: Session, listings: list[dict]) -> tuple[int, int]:
    """Upsert car listings into the database. Returns (new_count, updated_count)."""
    now = datetime.now(timezone.utc)
    new_count = 0
    updated_count = 0

    for data in listings:
        existing = db.query(Car).filter(Car.source_id == data["source_id"]).first()
        if existing:
            for key, value in data.items():
                if value is not None:
                    setattr(existing, key, value)
            existing.last_seen_at = now
            existing.is_active = True
            updated_count += 1
        else:
            car = Car(**data, last_seen_at=now)
            db.add(car)
            new_count += 1

    db.commit()
    return new_count, updated_count


def mark_inactive(db: Session, active_source_ids: list[str]):
    """Mark listings not seen in current scrape as inactive."""
    if active_source_ids:
        db.query(Car).filter(
            Car.source_id.notin_(active_source_ids),
            Car.is_active == True,
        ).update({"is_active": False}, synchronize_session=False)
        db.commit()


def run_scraper(max_pages: Optional[int] = None) -> dict:
    """Run the full scraping process. Returns stats dict."""
    db = SessionLocal()
    all_listings = []
    total_pages = 1

    try:
        listings, total_pages = scrape_page(1)
        all_listings.extend(listings)
        logger.info(f"Page 1: {len(listings)} listings, {total_pages} total pages")

        pages_to_scrape = min(total_pages, max_pages) if max_pages else total_pages
        for page in range(2, pages_to_scrape + 1):
            time.sleep(1.5)
            try:
                listings, _ = scrape_page(page)
                all_listings.extend(listings)
                logger.info(f"Page {page}: {len(listings)} listings")
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                continue

        active_ids = [l["source_id"] for l in all_listings]
        new_count, updated_count = upsert_cars(db, all_listings)
        mark_inactive(db, active_ids)

        logger.info("Scraping detail pages for trait fields...")

        detail_urls = [(l["source_id"], l["source_url"]) for l in all_listings if l.get("source_url")]
        max_detail = int(os.getenv("MAX_DETAIL_PAGES", "20"))
        detail_urls = detail_urls[:max_detail]
        logger.info(f"Scraping traits from {len(detail_urls)} detail pages (max {max_detail})")

        detail_count = 0
        failed = 0

        def fetch_detail(item):
            source_id, url = item
            time.sleep(0.3)
            traits = scrape_traits_from_detail(url)
            return source_id, traits

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(fetch_detail, item): item for item in detail_urls}
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    source_id, traits = future.result()
                    if traits:
                        car = db.query(Car).filter(Car.source_id == source_id).first()
                        if car:
                            for key, value in traits.items():
                                if value is not None:
                                    setattr(car, key, value)
                            detail_count += 1
                    if i % 10 == 0:
                        logger.info(f"  Detail progress: {i}/{len(detail_urls)}")
                except Exception as e:
                    failed += 1
                    logger.debug(f"Error scraping detail: {e}")

        if detail_count > 0:
            db.commit()

        logger.info(
            f"Scrape complete: {len(all_listings)} total, {new_count} new, "
            f"{updated_count} updated, {detail_count} details scraped, {failed} failed"
        )
        return {
            "total": len(all_listings),
            "new": new_count,
            "updated": updated_count,
            "pages_scraped": pages_to_scrape,
        }
    except Exception as e:
        logger.error(f"Scraper error: {e}")
        raise
    finally:
        db.close()
