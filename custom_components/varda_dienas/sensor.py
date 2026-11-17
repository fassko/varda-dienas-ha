"""Sensors for Latvian name days."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ALL_NAMES,
    ATTR_DATE,
    ATTR_EXTENDED_NAMES,
    ATTR_FAVORITES,
    ATTR_FAVORITE_TODAY,
    ATTR_FAVORITE_TOMORROW,
    ATTR_MONTH_DAY,
    ATTR_NAMES,
    ATTR_SHOW_EXTENDED,
    ATTR_TOMORROW_EXTENDED_NAMES,
    ATTR_TOMORROW_NAMES,
    DOMAIN,
)
from .coordinator import NameDayCoordinator, NameDaySnapshot
from .repository import date_key


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up name-day sensors."""
    coordinator: NameDayCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TodayNameDaySensor(coordinator, entry),
            TomorrowNameDaySensor(coordinator, entry),
            FavoritesTodaySensor(coordinator, entry),
        ]
    )


class NameDaySensorBase(CoordinatorEntity[NameDayCoordinator], SensorEntity):
    """Shared sensor helpers."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NameDayCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Vārda dienas",
            manufacturer="Latvia",
            model="Name day calendar",
        )

    @property
    def data(self) -> NameDaySnapshot:
        """Latest coordinator snapshot."""
        return self.coordinator.data


class TodayNameDaySensor(NameDaySensorBase):
    """Today's traditional name days."""

    def __init__(self, coordinator: NameDayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            SensorEntityDescription(
                key="today",
                translation_key="today",
                icon="mdi:calendar-today",
            ),
        )

    @property
    def native_value(self) -> str:
        """Comma-separated traditional names for today."""
        names = self.data.today_names.main
        return ", ".join(names) if names else "—"

    @property
    def extra_state_attributes(self) -> dict:
        """Expose extended/tomorrow/favorites for cards and automations."""
        today = self.data.today_names
        tomorrow = self.data.tomorrow_names
        return {
            ATTR_NAMES: list(today.main),
            ATTR_EXTENDED_NAMES: list(today.extended),
            ATTR_ALL_NAMES: list(today.all),
            ATTR_DATE: self.data.today.isoformat(),
            ATTR_MONTH_DAY: date_key(self.data.today),
            ATTR_TOMORROW_NAMES: list(tomorrow.main),
            ATTR_TOMORROW_EXTENDED_NAMES: list(tomorrow.extended),
            ATTR_FAVORITES: list(self.data.favorites),
            ATTR_FAVORITE_TODAY: list(self.data.favorite_today),
            ATTR_FAVORITE_TOMORROW: list(self.data.favorite_tomorrow),
            ATTR_SHOW_EXTENDED: self.data.show_extended,
        }


class TomorrowNameDaySensor(NameDaySensorBase):
    """Tomorrow's traditional name days."""

    def __init__(self, coordinator: NameDayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            SensorEntityDescription(
                key="tomorrow",
                translation_key="tomorrow",
                icon="mdi:calendar-arrow-right",
            ),
        )

    @property
    def native_value(self) -> str:
        """Comma-separated traditional names for tomorrow."""
        names = self.data.tomorrow_names.main
        return ", ".join(names) if names else "—"

    @property
    def extra_state_attributes(self) -> dict:
        """Expose tomorrow's extended names."""
        tomorrow = self.data.tomorrow_names
        return {
            ATTR_NAMES: list(tomorrow.main),
            ATTR_EXTENDED_NAMES: list(tomorrow.extended),
            ATTR_ALL_NAMES: list(tomorrow.all),
            ATTR_DATE: self.data.tomorrow.isoformat(),
            ATTR_MONTH_DAY: date_key(self.data.tomorrow),
            ATTR_FAVORITE_TOMORROW: list(self.data.favorite_tomorrow),
            ATTR_SHOW_EXTENDED: self.data.show_extended,
        }


class FavoritesTodaySensor(NameDaySensorBase):
    """Favorite names celebrating today."""

    def __init__(self, coordinator: NameDayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            SensorEntityDescription(
                key="favorites_today",
                translation_key="favorites_today",
                icon="mdi:star",
            ),
        )

    @property
    def native_value(self) -> str:
        """Comma-separated favorite names celebrating today."""
        names = self.data.favorite_today
        return ", ".join(names) if names else "none"

    @property
    def extra_state_attributes(self) -> dict:
        """List favorites and tomorrow's matches."""
        return {
            ATTR_NAMES: list(self.data.favorite_today),
            ATTR_FAVORITES: list(self.data.favorites),
            ATTR_FAVORITE_TOMORROW: list(self.data.favorite_tomorrow),
            ATTR_DATE: self.data.today.isoformat(),
        }
