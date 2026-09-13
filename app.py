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

st.markdown(
    """
    <style>

    /* -----------------------------
       Main App
    ----------------------------- */

    .stApp {
        background-color: #f7f9fc;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* -----------------------------
       Header
    ----------------------------- */

    .header-box {
        background: linear-gradient(
            135deg,
            #0f766e,
            #115e59
        );

        padding: 35px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }

    .header-title {
        color: white;
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .header-subtitle {
        color: #dff7f3;
        font-size: 17px;
    }


    /* -----------------------------
       Cards
    ----------------------------- */

    .card {
        background-color: white;
        padding: 24px;
        border-radius: 18px;
        border: 1px solid #e5eaf0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        margin-bottom: 18px;
    }


    /* -----------------------------
       Winner Card
    ----------------------------- */

    .winner-card {
        background: linear-gradient(
            135deg,
            #ecfdf5,
            #f0fdfa
        );

        padding: 28px;
        border-radius: 20px;
        border: 2px solid #99f6e4;
        margin-bottom: 25px;
    }

    .winner-title {
        color: #065f46;
        font-size: 26px;
        font-weight: 800;
    }

    .winner-price {
        color: #047857;
        font-size: 34px;
        font-weight: 800;
        margin-top: 10px;
    }


    /* -----------------------------
       Item Cards
    ----------------------------- */

    .item-card {
        background-color: white;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e5eaf0;
        margin-bottom: 12px;
    }

    .item-name {
        font-weight: 700;
        font-size: 16px;
        color: #17202a;
    }

    .item-price {
        font-weight: 800;
        color: #0f766e;
        font-size: 18px;
    }


    /* -----------------------------
       Combination Card
    ----------------------------- */

    .combination-card {
        background-color: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #dfe7ef;
        box-shadow: 0 5px 18px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .combination-total {
        color: #0f766e;
        font-size: 32px;
        font-weight: 800;
        margin-top: 8px;
    }


    /* -----------------------------
       Buttons
    ----------------------------- */

    .stButton > button {
        height: 50px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 700;
    }


    /* -----------------------------
       Text Area
    ----------------------------- */

    textarea {
        border-radius: 12px !important;
    }


    /* -----------------------------
       Footer
    ----------------------------- */

    .footer {
        text-align: center;
        color: #8a94a3;
        font-size: 13px;
        padding-top: 35px;
        padding-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA PATH
# =========================================================

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "store_prices.json"
)


# =========================================================
# LOAD STORES
# =========================================================

def load_stores():

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# =========================================================
# COMPARE ITEMS
# =========================================================

def compare_items(items):

    if not items:
        return None

    stores = load_stores()

    if not stores:
        return None

    store_results = []

    # -----------------------------------------------------
    # Compare each store
    # -----------------------------------------------------

    for store_key, store_info in stores.items():

        price_dict = store_info.get(
            "prices",
            {}
        )

        total = 0

        matched_items = []
        unmatched_items = []

        # -------------------------------------------------
        # Compare each grocery item
        # -------------------------------------------------

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
                    "matched_via": source
                })

            else:

                unmatched_items.append(
                    user_item
                )

        # -------------------------------------------------
        # Store result
        # -------------------------------------------------

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

            "unmatched_items": unmatched_items
        })


    # -----------------------------------------------------
    # Cheapest store first
    # -----------------------------------------------------

    store_results.sort(
        key=lambda store: store["total"]
    )


    # =====================================================
    # FIND BEST COMBINATION
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
                ):

                    if (
                        best_price is None
                        or matched_item["price"]
                        < best_price
                    ):

                        best_price = matched_item[
                            "price"
                        ]

                        best_store_name = store[
                            "name"
                        ]

        # -------------------------------------------------
        # Add cheapest item
        # -------------------------------------------------

        if best_price is not None:

            best_combo.append({
                "item": user_item,
                "store": best_store_name,
                "price": best_price
            })

            best_combo_total += best_price


    # =====================================================
    # RETURN
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
            )
    }


# =========================================================
# PROFESSIONAL HEADER
# =========================================================

st.markdown(
    """
    <div class="header-box">

        <div class="header-title">
            🛒 Grocery Lens
        </div>

        <div class="header-subtitle">
            Smart grocery price comparison made simple.
            Compare stores and find the best way to shop.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# GROCERY INPUT
# =========================================================

st.subheader("📝 Your Grocery List")

st.write(
    "Enter the grocery items you want to compare."
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
    height=180,
    label_visibility="collapsed"
)


st.caption(
    "💡 Enter one grocery item per line."
)


st.write("")


# =========================================================
# COMPARE BUTTON
# =========================================================

compare_button = st.button(
    "🔍 Compare Prices",
    use_container_width=True
)


# =========================================================
# RESULTS
# =========================================================

if compare_button:

    # -----------------------------------------------------
    # Convert text into list
    # -----------------------------------------------------

    items = [
        item.strip()
        for item in grocery_text.splitlines()
        if item.strip()
    ]


    # -----------------------------------------------------
    # Check empty input
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
                    f"Successfully compared "
                    f"{len(items)} grocery item(s)."
                )


                # =============================================
                # BEST SINGLE STORE
                # =============================================

                cheapest = result[
                    "cheapest_single_store"
                ]


                if cheapest:

                    st.subheader(
                        "🏆 Best Single Store"
                    )


                    st.markdown(
                        f"""
                        <div class="winner-card">

                            <div class="winner-title">
                                🏆 {cheapest["name"]}
                            </div>

                            <div>
                                📍 {cheapest["address"]}
                            </div>

                            <div class="winner-price">
                                Rs. {cheapest["total"]:.2f}
                            </div>

                            <div>
                                Total price for your grocery list
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # -----------------------------------------
                    # MATCHED ITEMS
                    # -----------------------------------------

                    if cheapest[
                        "matched_items"
                    ]:

                        st.markdown(
                            "#### 🛍️ Items Found"
                        )

                        columns = st.columns(2)

                        for index, item in enumerate(
                            cheapest["matched_items"]
                        ):

                            with columns[
                                index % 2
                            ]:

                                st.markdown(
                                    f"""
                                    <div class="item-card">

                                        <div class="item-name">
                                            {item["you_typed"]}
                                        </div>

                                        <div>
                                            Matched as:
                                            {item["matched_to"]}
                                        </div>

                                        <br>

                                        <div class="item-price">
                                            Rs. {item["price"]:.2f}
                                        </div>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )


                    # -----------------------------------------
                    # UNMATCHED ITEMS
                    # -----------------------------------------

                    if cheapest[
                        "unmatched_items"
                    ]:

                        st.warning(
                            "These items were not found: "
                            + ", ".join(
                                cheapest[
                                    "unmatched_items"
                                ]
                            )
                        )


                # =============================================
                # BEST COMBINATION
                # =============================================

                st.subheader(
                    "💰 Smart Shopping Combination"
                )


                st.write(
                    "For each item, Grocery Lens selects "
                    "the store offering the lowest price."
                )


                if result["best_combo"]:

                    for item in result[
                        "best_combo"
                    ]:

                        st.markdown(
                            f"""
                            <div class="item-card">

                                🛒
                                <b>{item["item"]}</b>

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
                        <div class="combination-card">

                            <div>
                                💎 Best possible combination
                            </div>

                            <div class="combination-total">
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
                        "No matching items were found."
                    )


                # =============================================
                # ALL STORES
                # =============================================

                st.subheader(
                    "🏪 Compare All Stores"
                )


                for index, store in enumerate(
                    result["all_stores"]
                ):

                    if index == 0:

                        label = (
                            f"🏆 {store['name']} "
                            f" — Rs. {store['total']:.2f}"
                        )

                    else:

                        label = (
                            f"🏪 {store['name']} "
                            f" — Rs. {store['total']:.2f}"
                        )


                    with st.expander(label):

                        # -------------------------------------
                        # Address
                        # -------------------------------------

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
                                "#### Items Found"
                            )

                            for item in store[
                                "matched_items"
                            ]:

                                st.write(
                                    f"✓ "
                                    f"{item['you_typed']} "
                                    f"→ "
                                    f"{item['matched_to']} "
                                    f"— "
                                    f"Rs. {item['price']:.2f}"
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


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="footer">

        🛒 Grocery Lens
        <br>
        Smart Grocery Price Comparison

    </div>
    """,
    unsafe_allow_html=True
)
