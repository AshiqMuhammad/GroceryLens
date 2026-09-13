"""
matching.py
1. fuzzy_match_item: match a user-typed item ("chawal") to a known price
   item ("rice") using local string matching first (free, instant, no API call).
2. groq_match_item: fallback that asks Groq's free LLM API to pick the closest
   known item when local matching fails (handles slang, Urdu transliteration,
   typos that difflib can't catch).
3. match_store_name: match a REAL store name from OpenStreetMap to one of
   our hardcoded price chains.
"""
import difflib
import json
import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # fast + free-tier friendly


def fuzzy_match_item(user_item, price_dict, cutoff=0.6):
    user_item = (user_item or "").strip().lower()
    if not user_item:
        return None, None

    known_items = list(price_dict.keys())

    if user_item in price_dict:
        return user_item, price_dict[user_item]

    close = difflib.get_close_matches(user_item, known_items, n=1, cutoff=cutoff)
    if close:
        matched_key = close[0]
        return matched_key, price_dict[matched_key]

    for key in known_items:
        if user_item in key or key in user_item:
            return key, price_dict[key]

    return None, None


def groq_match_item(user_item, price_dict, timeout=8):
    """
    Ask Groq to map a user-typed grocery item to one of our known item keys.
    Only called when local fuzzy_match_item fails. Returns (key, price) or
    (None, None) if Groq is unavailable, errors out, or finds no real match.
    This never invents a price — it only ever picks from price_dict's own keys.
    """
    if not GROQ_API_KEY:
        return None, None

    known_items = list(price_dict.keys())
    prompt = (
        "You match a grocery item name (possibly Urdu/Roman-Urdu transliteration, "
        "a brand name, or a typo) to the single closest item in this list:\n"
        f"{known_items}\n\n"
        f'Item to match: "{user_item}"\n\n'
        "Reply with ONLY the exact matching string from the list, or the word "
        "NONE if nothing in the list is a reasonable match. No punctuation, "
        "no explanation."
    )

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 20,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip().strip('"').lower()
    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError):
        return None, None

    if raw in price_dict:
        return raw, price_dict[raw]
    return None, None


def match_item(user_item, price_dict):
    """Try local matching first (free, instant); fall back to Groq only if needed."""
    key, price = fuzzy_match_item(user_item, price_dict)
    if key:
        return key, price, "local"
    key, price = groq_match_item(user_item, price_dict)
    if key:
        return key, price, "groq"
    return None, None, None


def match_store_name(osm_name, store_data):
    name = (osm_name or "").lower()
    for chain_key, chain_info in store_data.items():
        for keyword in chain_info.get("match_keywords", []):
            if keyword.lower() in name:
                return chain_key
    return None
