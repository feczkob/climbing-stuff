import atexit

from flask import Flask, render_template, abort, jsonify
from flask_apscheduler import APScheduler

from scrapers.service import fetch_all_discounts, DISCOUNTS_LOADED, ALL_DISCOUNTS, CATEGORIES, refresh_discounts_job

app = Flask(__name__)

def start_scheduler():
    refresh_discounts_job()
    scheduler = APScheduler()
    scheduler.init_app(app)  # No Flask app context needed here
    scheduler.start()
    scheduler.add_job(
        id='refresh_discounts',
        func=refresh_discounts_job,
        trigger='interval',
        hours=12,
        replace_existing=True
    )
    # Ensure scheduler shuts down cleanly
    atexit.register(lambda: scheduler.shutdown(wait=False))

start_scheduler()

@app.route("/")
def index():
    return render_template(
        "index.html",
        categories=CATEGORIES,
    )

@app.route('/discounts/<category>', methods=['GET'])
def get_discounts_by_category(category):
    discounts = ALL_DISCOUNTS.get(category)
    if discounts is None:
        abort(404, description="Category not found")
    return jsonify(discounts)

if __name__ == "__main__":
    app.run(debug=True)