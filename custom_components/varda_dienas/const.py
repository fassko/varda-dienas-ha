"""Constants for the Vārda dienas integration."""

from __future__ import annotations

DOMAIN = "varda_dienas"

CONF_SHOW_EXTENDED = "show_extended"
CONF_FAVORITES = "favorites"

DEFAULT_SHOW_EXTENDED = False
DEFAULT_FAVORITES: list[str] = []

ATTR_NAMES = "names"
ATTR_EXTENDED_NAMES = "extended_names"
ATTR_ALL_NAMES = "all_names"
ATTR_DATE = "date"
ATTR_MONTH_DAY = "month_day"
ATTR_TOMORROW_NAMES = "tomorrow_names"
ATTR_TOMORROW_EXTENDED_NAMES = "tomorrow_extended_names"
ATTR_FAVORITES = "favorites"
ATTR_FAVORITE_TODAY = "favorite_today"
ATTR_FAVORITE_TOMORROW = "favorite_tomorrow"
ATTR_SHOW_EXTENDED = "show_extended"

RIGA_TIME_ZONE = "Europe/Riga"

MAIN_DATA_FILE = "namedays.json"
EXTENDED_DATA_FILE = "namedays-extended.json"

FRONTEND_URL = f"/{DOMAIN}_frontend"
STATIC_REGISTERED = "static_registered"

SERVICE_ADD_FAVORITE = "add_favorite"
SERVICE_REMOVE_FAVORITE = "remove_favorite"
SERVICE_SET_FAVORITES = "set_favorites"

ATTR_NAME = "name"
ATTR_NAMES_SERVICE = "names"
