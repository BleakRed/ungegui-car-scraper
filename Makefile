.PHONY: install backend frontend docker-up docker-down scrape clean

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

scrape:
	cd backend && python -c "from app.scraper import run_scraper; run_scraper(max_pages=5)"

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	rm -rf backend/cars.db backend/data
	rm -rf frontend/node_modules frontend/dist
