import os
import json
import streamlit as st

from matching import match_item


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Grocery Lens",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background: #f7f9fc;
    }

    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Hero section */
    .hero {
        background: linear-gradient(
            135deg,
            #0f766e 0%,
            #115e59 100%
        );
        padding: 45px 50px;
        border-radius: 24px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 12px 30px rgba(15, 118, 110, 0.18);
    }

    .hero h1 {
        font-size: 42px;
        margin: 0;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .hero p {
        font-size: 18px;
        margin-top: 12px;
        opacity: 0.9;
    }

    /* Section titles */
    .section-title {
        font-size: 25px;
        font-weight: 750;
        color: #17202a;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    /* General card */
    .card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e8edf3;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.05);
        margin-bottom: 18px;
    }

    /* Store card */
    .store-card {
        background: white;
        padding: 24px;
        border-radius: 18px;
        border: 1px solid #e5eaf0;
        margin-bottom: 16px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.04);
    }

    .store-name {
        font-size: 21px;
        font-weight: 750;
        color: #17202a;
    }

    .store-address {
        color: #687385;
        font-size: 14px;
        margin-top: 5px;
    }

    .store-price {
        font-size: 26px;
        font-weight: 800;
        color: #0f766e;
    }

    /* Winner card */
    .winner {
        background: linear-gradient(
            135deg,
            #ecfdf5,
            #f0fdfa
        );
        border: 2px solid #99f6e4;
        padding: 28px;
        border-radius: 20px;
        margin-bottom: 25px;
    }

    .winner-title {
        font-size: 27px;
        font-weight: 800;
        color: #065f46;
    }

    .winner-price {
        font-size: 34px;
        font-weight: 850;
        color: #047857;
    }

    /* Combination card */
    .combo {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #dfe7ef;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.05);
        margin-top: 20px;
    }

    .combo-total {
        font-size: 32px;
        font-weight: 850;
        color: #0f766e;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #8a94a3;
        font-size: 13px;
        padding-top: 35px;
        padding-bottom: 20px;
    }

    /* Text area */
    textarea {
        border-radius: 14px !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        height: 48px;
        font-weight: 700;
        font-size: 16px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA
# =========================================================

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "store_prices.json"
)


def load_stores():

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# =========================================================
# COMPARISON LOGIC
# =========================================================

def compare_items(items):

    if not items:
        return None

    stores = load_stores()

    if not stores:
        return None

    store_results = []

    for store_key, store_info in stores.items():

        price_dict = store_info.get(
            "prices",
            {}
        )

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

                unmatched_items.append(
                    user_item
                )

        store_results.append({
            "name": store_info.get(
                "display_name",
                store_key
            ),

            "address": store_info.get(
                "address",
                ""
            ),

            "total": round(
                total,
                2
            ),

            "matched_items": matched_items,

            "unmatched_items": unmatched_items,
        })


    # =====================================================
    # CHEAPEST STORE FIRST
    # =====================================================

    store_results.sort(
        key=lambda s: s["total"]
    )


    # =====================================================
    # BEST COMBINATION
    # =====================================================

    best_combo = []

    best_combo_total = 0

    for user_item in items:

        best_price = None
        best_store_name = None

        for store in store_results:

            for matched_item in store[
                "matched_items"
            ]:

                if (
                    matched_item["you_typed"]
                    == user_item
                    and (
                        best_price is None
                        or matched_item["price"]
                        < best_price
                    )
                ):

                    best_price = matched_item[
                        "price"
                    ]

                    best_store_name = store[
                        "name"
                    ]

        if best_price is not None:

            best_combo.append({
                "item": user_item,
                "store": best_store_name,
                "price": best_price
            })

            best_combo_total += best_price


    # =====================================================
    # RETURN RESULTS
    # =====================================================

    return {
        "cheapest_single_store":
            store_results[0]
            if store_results
            else None,

        "all_stores":
            store_results,

        "best_combo":
            best_combo,

        "best_combo_total":
            round(
                best_combo_total,
                2
            ),
    }


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">

    <h1>🛒 Grocery Lens</h1>

    <p>
        Compare grocery prices across stores
        and find the smartest way to shop.
    </p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# INPUT SECTION
# =========================================================

st.markdown(
    '<div class="section-title">📝 Your Grocery List</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="card">',
    unsafe_allow_html=True
)

grocery_text = st.text_area(
    "Grocery items",
    placeholder=(
        "Milk\n"
        "Bread\n"
        "Eggs\n"
        "Sugar\n"
        "Rice"
    ),
    height=170,
    label_visibility="collapsed"
)

st.caption(
    "💡 Enter one grocery item per line."
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# COMPARE BUTTON
# =========================================================

compare_button = st.button(
    "🔍  Compare Prices",
    use_container_width=True
)


# =========================================================
# RESULTS
# =========================================================

if compare_button:

    # -----------------------------------------------------
    # Convert input into list
    # -----------------------------------------------------

    items = [
        item.strip()
        for item in grocery_text.splitlines()
        if item.strip()
    ]


    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not items:

        st.error(
            "Please add at least one grocery item."
        )

    else:

        try:

            # -------------------------------------------------
            # Run comparison
            # -------------------------------------------------

            result = compare_items(items)


            # -------------------------------------------------
            # No stores
            # -------------------------------------------------

            if result is None:

                st.error(
                    "No stores are available."
                )


            else:

                st.success(
                    f"Comparison completed for "
                    f"{len(items)} item(s)."
                )


                # =============================================
                # CHEAPEST SINGLE STORE
                # =============================================

                cheapest = result[
                    "cheapest_single_store"
                ]


                if cheapest:

                    st.markdown(
                        '<div class="section-title">'
                        '🏆 Best Single Store'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    st.markdown(
                        f"""
                        <div class="winner">

                            <div class="winner-title">
                                🏆 {cheapest["name"]}
                            </div>

                            <div class="store-address">
                                📍 {cheapest["address"]}
                            </div>

                            <br>

                            <div class="winner-price">
                                Rs. {cheapest["total"]:.2f}
                            </div>

                            <div>
                                Estimated total for your
                                grocery list
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # -----------------------------------------
                    # Matched items
                    # -----------------------------------------

                    if cheapest[
                        "matched_items"
                    ]:

                        st.markdown(
                            "#### 🛍️ Items Found"
                        )

                        cols = st.columns(2)

                        for index, item in enumerate(
                            cheapest["matched_items"]
                        ):

                            with cols[
                                index % 2
                            ]:

                                st.markdown(
                                    f"""
                                    <div class="store-card">

                                        <b>
                                            {item["you_typed"]}
                                        </b>

                                        <br><br>

                                        Matched as:
                                        {item["matched_to"]}

                                        <br><br>

                                        <b>
                                            Rs. {item["price"]:.2f}
                                        </b>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )


                    # -----------------------------------------
                    # Unmatched items
                    # -----------------------------------------

                    if cheapest[
                        "unmatched_items"
                    ]:

                        st.warning(
                            "Not found: "
                            + ", ".join(
                                cheapest[
                                    "unmatched_items"
                                ]
                            )
                        )


                # =============================================
                # BEST COMBINATION
                # =============================================

                st.markdown(
                    '<div class="section-title">'
                    '💰 Smart Shopping Combination'
                    '</div>',
                    unsafe_allow_html=True
                )


                st.markdown(
                    """
                    <div class="card">

                        Buy each item from the store
                        where that item has the lowest price.

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                if result["best_combo"]:

                    for item in result[
                        "best_combo"
                    ]:

                        st.markdown(
                            f"""
                            <div class="store-card">

                                🛒
                                <b>
                                    {item["item"]}
                                </b>

                                &nbsp;&nbsp;→&nbsp;&nbsp;

                                🏪
                                {item["store"]}

                                <span style="
                                    float:right;
                                    font-weight:700;
                                    color:#0f766e;
                                ">

                                    Rs. {item["price"]:.2f}

                                </span>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    st.markdown(
                        f"""
                        <div class="combo">

                            <div>
                                💎 Best possible combination
                            </div>

                            <div class="combo-total">
                                Rs. {
                                    result["best_combo_total"]
                                :.2f}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                else:

                    st.info(
                        "No matching items found."
                    )


                # =============================================
                # ALL STORES
                # =============================================

                st.markdown(
                    '<div class="section-title">'
                    '🏪 Compare All Stores'
                    '</div>',
                    unsafe_allow_html=True
                )


                for index, store in enumerate(
                    result["all_stores"]
                ):

                    # First store is cheapest
                    if index == 0:

                        label = (
                            f"🏆 {store['name']} "
                            f" — Rs. "
                            f"{store['total']:.2f}"
                        )

                    else:

                        label = (
                            f"🏪 {store['name']} "
                            f" — Rs. "
                            f"{store['total']:.2f}"
                        )


                    with st.expander(label):

                        if store["address"]:

                            st.caption(
                                f"📍 {store['address']}"
                            )


                        # -------------------------------------
                        # Matched items
                        # -------------------------------------

                        if store[
                            "matched_items"
                        ]:

                            st.markdown(
                                "**Items Found**"
                            )

                            for item in store[
                                "matched_items"
                            ]:

                                st.write(
                                    f"✓ "
                                    f"{item['you_typed']} "
                                    f"→ "
                                    f"{item['matched_to']} "
                                    f"— Rs. "
                                    f"{item['price']:.2f}"
                                )


                        # -------------------------------------
                        # Unmatched items
                        # -------------------------------------

                        if store[
                            "unmatched_items"
                        ]:

                            st.warning(
                                "Not found: "
                                + ", ".join(
                                    store[
                                        "unmatched_items"
                                    ]
                                )
                            )


        # =====================================================
        # ERROR HANDLING
        # =====================================================

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        🛒 Grocery Lens
        <br>
        Smart grocery price comparison

    </div>
    """,
    unsafe_allow_html=True
)
