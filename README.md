# Climbing stuff discount Aggregator

This app aggregates discounts on climbing stuffs from multiple e-commerce sites using pluggable scrapers. It provides a simple web UI and a REST API for browsing discounts by category.

## Features

- **Multiple Scrapers:** Easily extensible scrapers for each supported site (e.g., Bergfreunde, Mountex).
- **Web UI:** Simple frontend to browse discounts by category.
- **REST API:** Fetch discounts for a given category via `/discounts/{category}`.
- **Configurable:** Add or remove sites and categories via YAML config files.

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv climbing-stuff
   source climbing-stuff/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure categories:**
   - Edit `config/categories.yaml` to manage categories and their URLs per site.

4. **Run the app:**
   ```bash
   python src/app/main.py
   ```

5. **Browse the UI:**
   - Open [http://localhost:5000](http://localhost:5000) in your browser.

## REST API

- **Endpoint:** `/discounts/{category}`
- **Method:** `GET`
- **Response:** JSON array of discounts for the given category.

Example:
```bash
curl http://localhost:5000/discounts/friends
```

## Adding New Scrapers

- Implement a new scraper class in the `src/scrapers/` directory.
- Register it in the `ScraperManager` in `src/core/manager.py`.
- Add its URLs to the relevant categories in `config/categories.yaml`.

## Project Structure

- `src/app/main.py` — Main Flask app (REST API & web UI)
- `src/scrapers/` — Site-specific scrapers
- `src/core/` — Core business logic and management
- `src/services/` — Service layer for discount operations
- `config/` — YAML config files for categories
- `templates/` — HTML templates for the web UI

---

**Note:** Some scrapers use Selenium and require ChromeDriver installed.
