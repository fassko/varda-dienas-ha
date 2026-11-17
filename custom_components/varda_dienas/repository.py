"""Latvian name-day calendar repository (bundled JSON)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

from .const import EXTENDED_DATA_FILE, MAIN_DATA_FILE

_DATA_DIR = Path(__file__).parent


@dataclass(frozen=True, slots=True)
class DayNames:
    """Names for a single calendar day."""

    main: tuple[str, ...]
    extended: tuple[str, ...]

    @property
    def all(self) -> tuple[str, ...]:
        """Main names followed by extended-only names."""
        return self.main + self.extended


def date_key(day: date) -> str:
    """Return MM-DD key used in the bundled calendars."""
    return f"{day.month:02d}-{day.day:02d}"


def _load_calendar(filename: str) -> dict[str, list[str]]:
    path = _DATA_DIR / filename
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    return {key: list(values) for key, values in raw.items()}


@lru_cache(maxsize=1)
def _calendars() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    return _load_calendar(MAIN_DATA_FILE), _load_calendar(EXTENDED_DATA_FILE)


class NameDayRepository:
    """Lookup helpers for traditional and extended Latvian name days."""

    def __init__(self) -> None:
        main, extended = _calendars()
        self._main = main
        self._extended = extended

    def names_for(self, day: date) -> DayNames:
        """Return main and extended-only names for a date."""
        key = date_key(day)
        main = tuple(self._main.get(key, []))
        main_folded = {name.casefold() for name in main}
        extended = tuple(
            name
            for name in self._extended.get(key, [])
            if name.casefold() not in main_folded
        )
        return DayNames(main=main, extended=extended)

    def find_dates_for_name(self, name: str) -> list[str]:
        """Return MM-DD keys where the name appears (main or extended)."""
        needle = name.casefold()
        found: list[str] = []
        for key in sorted(set(self._main) | set(self._extended)):
            names = self._main.get(key, []) + self._extended.get(key, [])
            if any(candidate.casefold() == needle for candidate in names):
                found.append(key)
        return found

    def known_names(self) -> list[str]:
        """Sorted unique names across both calendars."""
        names: set[str] = set()
        for values in self._main.values():
            names.update(values)
        for values in self._extended.values():
            names.update(values)
        return sorted(names, key=lambda value: value.casefold())

    def normalize_favorites(self, favorites: list[str] | tuple[str, ...] | set[str]) -> list[str]:
        """Deduplicate favorites while preserving first-seen casing."""
        seen: set[str] = set()
        result: list[str] = []
        for raw in favorites:
            name = raw.strip()
            if not name:
                continue
            key = name.casefold()
            if key in seen:
                continue
            seen.add(key)
            result.append(name)
        return result

    def matching_favorites(
        self, day: date, favorites: list[str], *, include_extended: bool = True
    ) -> list[str]:
        """Return configured favorites that celebrate on the given day."""
        day_names = self.names_for(day)
        pool = day_names.all if include_extended else day_names.main
        pool_folded = {name.casefold(): name for name in pool}
        matches: list[str] = []
        for favorite in favorites:
            key = favorite.casefold()
            if key in pool_folded:
                matches.append(pool_folded[key])
        return matches
