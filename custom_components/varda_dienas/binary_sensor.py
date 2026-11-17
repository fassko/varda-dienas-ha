"""Binary sensors for favorite name-day reminders."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_FAVORITE_TODAY, ATTR_FAVORITE_TOMORROW, ATTR_NAMES, DOMAIN
from .coordinator import NameDayCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up favorite binary sensors."""
    coordinator: NameDayCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FavoriteTodayBinarySensor(coordinator, entry),
            FavoriteTomorrowBinarySensor(coordinator, entry),
        ]
    )


class FavoriteBinarySensorBase(
    CoordinatorEntity[NameDayCoordinator], BinarySensorEntity
):
    """Shared favorite binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NameDayCoordinator,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
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


class FavoriteTodayBinarySensor(FavoriteBinarySensorBase):
    """On when a configured favorite celebrates today."""

    def __init__(self, coordinator: NameDayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="favorite_today",
                translation_key="favorite_today",
                icon="mdi:cake-variant",
            ),
        )

    @property
    def is_on(self) -> bool:
        """Return True when at least one favorite celebrates today."""
        return bool(self.coordinator.data.favorite_today)

    @property
    def extra_state_attributes(self) -> dict:
        """Names celebrating today."""
        return {
            ATTR_NAMES: list(self.coordinator.data.favorite_today),
            ATTR_FAVORITE_TODAY: list(self.coordinator.data.favorite_today),
        }


class FavoriteTomorrowBinarySensor(FavoriteBinarySensorBase):
    """On when a configured favorite celebrates tomorrow."""

    def __init__(self, coordinator: NameDayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(
            coordinator,
            entry,
            BinarySensorEntityDescription(
                key="favorite_tomorrow",
                translation_key="favorite_tomorrow",
                icon="mdi:cake",
            ),
        )

    @property
    def is_on(self) -> bool:
        """Return True when at least one favorite celebrates tomorrow."""
        return bool(self.coordinator.data.favorite_tomorrow)

    @property
    def extra_state_attributes(self) -> dict:
        """Names celebrating tomorrow."""
        return {
            ATTR_NAMES: list(self.coordinator.data.favorite_tomorrow),
            ATTR_FAVORITE_TOMORROW: list(self.coordinator.data.favorite_tomorrow),
        }
