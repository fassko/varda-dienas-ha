"""Calendar entities for Latvian name days."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import NameDayCoordinator
from .repository import date_key


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up name-day calendars."""
    coordinator: NameDayCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AllNameDaysCalendar(coordinator, entry),
            FavoritesCalendar(coordinator, entry),
        ]
    )


class NameDayCalendarBase(CoordinatorEntity[NameDayCoordinator], CalendarEntity):
    """Shared calendar helpers."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NameDayCoordinator,
        entry: ConfigEntry,
        key: str,
        translation_key: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = translation_key
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Vārda dienas",
            manufacturer="Latvia",
            model="Name day calendar",
        )

    def _iter_days(self, start: date, end: date):
        current = start
        while current < end:
            yield current
            current += timedelta(days=1)

    def _as_date(self, value: datetime | date) -> date:
        if isinstance(value, datetime):
            return dt_util.as_local(value).date()
        return value


class AllNameDaysCalendar(NameDayCalendarBase):
    """Full Latvian name-day calendar."""

    def __init__(self, coordinator: NameDayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            key="calendar",
            translation_key="calendar",
            icon="mdi:calendar-month",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Next or current day's name-day event."""
        today = self.coordinator.today()
        events = self._events_for_range(today, today + timedelta(days=14))
        return events[0] if events else None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return name-day events in the requested range."""
        return self._events_for_range(
            self._as_date(start_date), self._as_date(end_date)
        )

    def _events_for_range(self, start: date, end: date) -> list[CalendarEvent]:
        include_extended = self.coordinator.show_extended
        events: list[CalendarEvent] = []
        for day in self._iter_days(start, end):
            day_names = self.coordinator.repository.names_for(day)
            names = day_names.all if include_extended else day_names.main
            if not names:
                continue
            summary = ", ".join(names)
            description = f"Vārda diena · {date_key(day)}"
            if include_extended and day_names.extended:
                description += (
                    f"\nTradicionālie: {', '.join(day_names.main)}"
                    f"\nPapildu: {', '.join(day_names.extended)}"
                )
            events.append(
                CalendarEvent(
                    summary=summary,
                    start=day,
                    end=day + timedelta(days=1),
                    description=description,
                    uid=f"varda-dienas-{date_key(day)}",
                )
            )
        return events


class FavoritesCalendar(NameDayCalendarBase):
    """Calendar containing only configured favorite names."""

    def __init__(self, coordinator: NameDayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            key="favorites_calendar",
            translation_key="favorites_calendar",
            icon="mdi:calendar-star",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Next upcoming favorite name day."""
        today = self.coordinator.today()
        events = self._events_for_range(today, today + timedelta(days=400))
        return events[0] if events else None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return favorite name-day events in the requested range."""
        return self._events_for_range(
            self._as_date(start_date), self._as_date(end_date)
        )

    def _events_for_range(self, start: date, end: date) -> list[CalendarEvent]:
        favorites = self.coordinator.favorites
        if not favorites:
            return []

        events: list[CalendarEvent] = []
        for day in self._iter_days(start, end):
            matches = self.coordinator.repository.matching_favorites(
                day, favorites, include_extended=True
            )
            if not matches:
                continue
            summary = ", ".join(matches)
            events.append(
                CalendarEvent(
                    summary=summary,
                    start=day,
                    end=day + timedelta(days=1),
                    description=f"Mīļākā vārda diena · {date_key(day)}",
                    uid=f"varda-dienas-fav-{date_key(day)}",
                )
            )
        return events
