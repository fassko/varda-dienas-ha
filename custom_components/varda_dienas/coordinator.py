"""Data update coordinator for Vārda dienas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_FAVORITES,
    CONF_SHOW_EXTENDED,
    DEFAULT_FAVORITES,
    DEFAULT_SHOW_EXTENDED,
    DOMAIN,
    RIGA_TIME_ZONE,
)
from .repository import DayNames, NameDayRepository


@dataclass(frozen=True, slots=True)
class NameDaySnapshot:
    """Computed name-day state for today and tomorrow."""

    today: date
    tomorrow: date
    today_names: DayNames
    tomorrow_names: DayNames
    favorites: list[str]
    show_extended: bool
    favorite_today: list[str]
    favorite_tomorrow: list[str]


class NameDayCoordinator(DataUpdateCoordinator[NameDaySnapshot]):
    """Refresh name-day snapshot around local midnight."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(minutes=30),
        )
        self.entry = entry
        self.repository = NameDayRepository()
        self._tz = ZoneInfo(RIGA_TIME_ZONE)

    @property
    def favorites(self) -> list[str]:
        """Configured favorite names."""
        raw = self.entry.options.get(
            CONF_FAVORITES, self.entry.data.get(CONF_FAVORITES, DEFAULT_FAVORITES)
        )
        if isinstance(raw, str):
            raw = [part.strip() for part in raw.replace(";", ",").split(",")]
        return self.repository.normalize_favorites(list(raw or []))

    @property
    def show_extended(self) -> bool:
        """Whether extended names are included in entities/card defaults."""
        return bool(
            self.entry.options.get(
                CONF_SHOW_EXTENDED,
                self.entry.data.get(CONF_SHOW_EXTENDED, DEFAULT_SHOW_EXTENDED),
            )
        )

    def now_local(self) -> datetime:
        """Current time in Europe/Riga."""
        return datetime.now(tz=self._tz)

    def today(self) -> date:
        """Today's date in Europe/Riga."""
        return self.now_local().date()

    async def _async_update_data(self) -> NameDaySnapshot:
        today = self.today()
        tomorrow = today + timedelta(days=1)
        favorites = self.favorites
        show_extended = self.show_extended
        today_names = self.repository.names_for(today)
        tomorrow_names = self.repository.names_for(tomorrow)
        return NameDaySnapshot(
            today=today,
            tomorrow=tomorrow,
            today_names=today_names,
            tomorrow_names=tomorrow_names,
            favorites=favorites,
            show_extended=show_extended,
            favorite_today=self.repository.matching_favorites(
                today, favorites, include_extended=True
            ),
            favorite_tomorrow=self.repository.matching_favorites(
                tomorrow, favorites, include_extended=True
            ),
        )
