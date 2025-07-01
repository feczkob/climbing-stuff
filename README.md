# Climbing Equipment Discount Aggregator

This app aggregates discounts on climbing equipment from multiple e-commerce sites using pluggable scrapers. It provides a simple web UI and a REST API for browsing discounts by category.

## Features

- **Multiple Scrapers:** Easily extensible scrapers for each supported site (e.g., Bergfreunde, Mountex).
- **Web UI:** Simple frontend to browse discounts by category.
- **REST API:** Fetch discounts for a given category via `/discounts/{category}`.
- **Configurable:** Add or remove sites and categories via YAML config files.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure sites and categories:**
   - Edit `config/sites.yaml` to enable/disable sites.
   - Edit `config/categories.yaml` to manage categories and their URLs per site.

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Browse the UI:**
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

- Implement a new scraper class in the `scrapers/` directory.
- Register it in the `SCRAPER_MAP` in `app.py`.
- Add its URLs to the relevant categories in `config/categories.yaml`.

## Project Structure

- `app.py` — Main Flask app (REST API & web UI)
- `scrapers/` — Site-specific scrapers
- `config/` — YAML config files for sites and categories
- `templates/` — HTML templates for the web UI

---

**Note:** Some scrapers use Selenium and require ChromeDriver installed.
