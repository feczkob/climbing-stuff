# Climbing Equipment Discount Notifier

This app periodically scans climbing equipment e-commerce sites for discounts and sends WhatsApp notifications when discounts are found.

## Features
- Pluggable scrapers for each site
- Telegram notifications
- Configurable site list
- Easy to extend with new sites

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure in `notifier/`
3. Add sites to `config/sites.yaml`
4. Run the app: `python main.py` 