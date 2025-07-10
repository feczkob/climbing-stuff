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

## Running the Application

You can run the application in either development (non-production) or production mode.

### Development Mode (Non-Production)

In development mode, the application uses mock scrapers that read from local HTML files for faster testing and development. This is the default mode.

To run in development mode:
```bash
python3 run_app.py
```

### Production Mode

In production mode, the application uses live scrapers to fetch real-time data from the websites.

To run in production mode, set the `PRODUCTION_MODE` environment variable to `true`:
```bash
PRODUCTION_MODE=true python3 run_app.py
```

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
## Running Tests

### E2E Tests

To run the end-to-end tests, use the following command:

```bash
npx playwright test
```

This will run the tests and open an HTML report in your browser.

To run the tests without opening the browser report and see the output directly in the terminal, use the `list` reporter:

```bash
npx playwright test --reporter=list
```
