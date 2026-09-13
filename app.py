import os
import json
import streamlit as st

from matching import match_item


# --------------------------------------------------
# Page Settings
# --------------------------------------------------

st.set_page_config(
    page_title="Grocery Lens",
    page_icon="🛒",
    layout="centered"
)


# --------------------------------------------------
# Data Path
# --------------------------------------------------

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "store_prices.json"
)


# --------------------------------------------------
# Load Stores
# --------------------------------------------------

def load_stores():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------
# Compare Grocery Items
# --------------------------------------------------

def compare_items(items):

    if not items:
        return None

    stores = load_stores()

    if not stores:
        return None

    store_results = []

    for store_key, store_info in stores.items():

        price_dict = store_info.get("prices", {})

        total = 0

        matched_items = []
        unmatched_items = []

        for user_item in items:

            matched_key, price, source = match_item(
                user_item,
                price_dict
            )

            if matched_key:

                total += price

                matched_items.append({
                    "you_typed": user_item,
                    "matched_to": matched_key,
                    "price": price,
                    "matched_via": source,
                })

            else:

                unmatched_items.append(user_item)

        store_results.append({
            "name": store_info.get(
                "display_name",
                store_key
            ),

            "address": store_info.get(
                "address",
                ""
            ),

            "total": round(total, 2),

            "matched_items": matched_items,

            "unmatched_items": unmatched_items,
        })

    # Cheapest store first
    store_results.sort(
        key=lambda s: s["total"]
    )


    # --------------------------------------------------
    # Best Combination
    # --------------------------------------------------

    best_combo = []

    best_combo_total = 0

    for user_item in items:

        best_price = None
        best_store_name = None

        for store in store_results:

            for matched_item in store["matched_items"]:

                if (
                    matched_item["you_typed"] == user_item
                    and (
                        best_price is None
                        or matched_item["price"] < best_price
                    )
                ):

                    best_price = matched_item["price"]

                    best_store_name = store["name"]

        if best_price is not None:

            best_combo.append({
                "item": user_item,
                "store": best_store_name,
                "price": best_price
            })

            best_combo_total += best_price


    return {
        "cheapest_single_store": (
            store_results[0]
            if store_results
            else None
        ),

        "all_stores": store_results,

        "best_combo": best_combo,

        "best_combo_total": round(
            best_combo_total,
            2
        ),
    }


# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("🛒 Grocery Lens")

st.subheader("Grocery Price Comparator")

st.write(
    "Enter your grocery items and compare prices "
    "across all available stores."
)


# --------------------------------------------------
# Grocery Input
# --------------------------------------------------

grocery_text = st.text_area(
    "Enter grocery items",
    placeholder="Example:\nMilk\nBread\nEggs\nSugar",
    height=150
)


# --------------------------------------------------
# Compare Button
# --------------------------------------------------

if st.button(
    "🔍 Compare Prices",
    use_container_width=True
):

    # Convert text into list
    items = [
        item.strip()
        for item in grocery_text.splitlines()
        if item.strip()
    ]

    # Check input
    if not items:

        st.error(
            "Please add at least one grocery item."
        )

    else:

        try:

            result = compare_items(items)

            if result is None:

                st.error(
                    "No stores are available."
                )

            else:

                # --------------------------------------------------
                # Cheapest Single Store
                # --------------------------------------------------

                cheapest_store = result[
                    "cheapest_single_store"
                ]

                st.success(
                    "Comparison completed successfully!"
                )

                st.header(
                    "🏆 Cheapest Single Store"
                )

                if cheapest_store:

                    st.write(
                        f"### {cheapest_store['name']}"
                    )

                    if cheapest_store["address"]:

                        st.write(
                            f"📍 {cheapest_store['address']}"
                        )

                    st.metric(
                        "Total Price",
                        f"Rs. {cheapest_store['total']:.2f}"
                    )


                    # Matched items
                    if cheapest_store[
                        "matched_items"
                    ]:

                        st.subheader(
                            "Matched Items"
                        )

                        for item in cheapest_store[
                            "matched_items"
                        ]:

                            st.write(
                                f"✅ {item['you_typed']} "
                                f"→ {item['matched_to']} "
                                f"= Rs. {item['price']:.2f}"
                            )


                    # Unmatched items
                    if cheapest_store[
                        "unmatched_items"
                    ]:

                        st.warning(
                            "Items not found: "
                            + ", ".join(
                                cheapest_store[
                                    "unmatched_items"
                                ]
                            )
                        )


                # --------------------------------------------------
                # All Stores
                # --------------------------------------------------

                st.header(
                    "🏪 All Stores"
                )

                for store in result[
                    "all_stores"
                ]:

                    with st.expander(
                        f"{store['name']} — "
                        f"Rs. {store['total']:.2f}"
                    ):

                        if store["address"]:

                            st.write(
                                f"📍 {store['address']}"
                            )

                        if store["matched_items"]:

                            for item in store[
                                "matched_items"
                            ]:

                                st.write(
                                    f"✅ {item['you_typed']} "
                                    f"→ {item['matched_to']} "
                                    f"= Rs. {item['price']:.2f}"
                                )

                        if store["unmatched_items"]:

                            st.warning(
                                "Not found: "
                                + ", ".join(
                                    store[
                                        "unmatched_items"
                                    ]
                                )
                            )


                # --------------------------------------------------
                # Best Combination
                # --------------------------------------------------

                st.header(
                    "💰 Best Combination"
                )

                st.write(
                    "Buy each item from the store "
                    "where it is cheapest."
                )

                if result["best_combo"]:

                    for item in result[
                        "best_combo"
                    ]:

                        st.write(
                            f"🛒 {item['item']} "
                            f"→ {item['store']} "
                            f"= Rs. {item['price']:.2f}"
                        )

                    st.success(
                        f"Best Combination Total: "
                        f"Rs. {result['best_combo_total']:.2f}"
                    )

                else:

                    st.warning(
                        "No matching items found."
                    )


        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )
