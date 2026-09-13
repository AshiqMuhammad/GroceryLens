"""
app.py — Flask backend for the Grocery Price Comparator.

No location, no external API — everything comes from data/store_prices.json,
which you edit by hand to add/update stores and prices. The app just compares
your grocery list across every store defined there.
"""
import os
import json

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from matching import match_item

load_dotenv()

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "store_prices.json")


def load_stores():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/compare", methods=["POST"])
def compare():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items", [])

    if not items or not isinstance(items, list):
        return jsonify({"error": "Please add at least one grocery item."}), 400

    stores = load_stores()
    if not stores:
        return jsonify({"error": "No stores are set up yet. Add some to data/store_prices.json."}), 500

    store_results = []
    for store_key, store_info in stores.items():
        price_dict = store_info.get("prices", {})
        total = 0
        matched_items, unmatched_items = [], []
        for user_item in items:
            matched_key, price, source = match_item(user_item, price_dict)
            if matched_key:
                total += price
                matched_items.append({
                    "you_typed": user_item, "matched_to": matched_key,
                    "price": price, "matched_via": source,
                })
            else:
                unmatched_items.append(user_item)

        store_results.append({
            "name": store_info.get("display_name", store_key),
            "address": store_info.get("address", ""),
            "total": round(total, 2),
            "matched_items": matched_items,
            "unmatched_items": unmatched_items,
        })

    store_results.sort(key=lambda s: s["total"])

    best_combo, best_combo_total = [], 0
    for user_item in items:
        best_price, best_store_name = None, None
        for s in store_results:
            for mi in s["matched_items"]:
                if mi["you_typed"] == user_item and (best_price is None or mi["price"] < best_price):
                    best_price, best_store_name = mi["price"], s["name"]
        if best_price is not None:
            best_combo.append({"item": user_item, "store": best_store_name, "price": best_price})
            best_combo_total += best_price

    return jsonify({
        "cheapest_single_store": store_results[0] if store_results else None,
        "all_stores": store_results,
        "best_combo": best_combo,
        "best_combo_total": round(best_combo_total, 2),
    })


if __name__ == "__main__":
    import webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")

    Timer(1.5, open_browser).start()

    app.run(debug=True)