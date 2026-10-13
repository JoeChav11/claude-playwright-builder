"""Test data. Edit the JSON files, not this module.

    from data import USERS, PRODUCTS, CUSTOMERS
    USERS["standard"]["username"]  -> "standard_user"
"""
import json
from pathlib import Path

_DIR = Path(__file__).parent


def _load(name: str) -> dict:
    return json.loads((_DIR / f"{name}.json").read_text(encoding="utf-8"))


USERS = _load("users")
PRODUCTS = _load("products")
CUSTOMERS = _load("customers")


def money(amount: float) -> str:
    """Format a price the way the site shows it: 29.99 -> "$29.99"."""
    return f"${amount:.2f}"
