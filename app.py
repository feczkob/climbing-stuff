from flask import Flask, render_template, abort, jsonify

from scrapers.service import fetch_all_discounts, DISCOUNTS_LOADED, ALL_DISCOUNTS, CATEGORIES

app = Flask(__name__)

@app.before_request
def load_discounts_to_memory():
    global ALL_DISCOUNTS, DISCOUNTS_LOADED, CATEGORIES
    if not DISCOUNTS_LOADED:
        ALL_DISCOUNTS, CATEGORIES = fetch_all_discounts()
        DISCOUNTS_LOADED = True

@app.route("/")
def index():
    return render_template(
        "index.html",
        all_discounts=ALL_DISCOUNTS,
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