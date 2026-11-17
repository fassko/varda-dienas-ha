"""Services for managing favorite names."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_NAME,
    ATTR_NAMES_SERVICE,
    CONF_FAVORITES,
    CONF_SHOW_EXTENDED,
    DOMAIN,
    SERVICE_ADD_FAVORITE,
    SERVICE_REMOVE_FAVORITE,
    SERVICE_SET_FAVORITES,
)
from .coordinator import NameDayCoordinator
from .repository import NameDayRepository

_LOGGER = logging.getLogger(__name__)

_SERVICES_REGISTERED = "services_registered"

SERVICE_NAME_SCHEMA = vol.Schema({vol.Required(ATTR_NAME): cv.string})
SERVICE_NAMES_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NAMES_SERVICE): vol.All(cv.ensure_list, [cv.string]),
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register favorite management services once."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(_SERVICES_REGISTERED):
        return

    async def _update_favorites(mutator) -> None:
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            _LOGGER.warning("No Vārda dienas config entry found")
            return
        entry = entries[0]
        coordinator: NameDayCoordinator | None = hass.data.get(DOMAIN, {}).get(
            entry.entry_id
        )
        repo = coordinator.repository if coordinator else NameDayRepository()
        current = list(
            (coordinator.favorites if coordinator else entry.options.get(CONF_FAVORITES, []))
        )
        updated = repo.normalize_favorites(mutator(current))
        new_options = {
            **entry.options,
            CONF_FAVORITES: updated,
            CONF_SHOW_EXTENDED: entry.options.get(
                CONF_SHOW_EXTENDED,
                entry.data.get(CONF_SHOW_EXTENDED, False),
            ),
        }
        hass.config_entries.async_update_entry(entry, options=new_options)

    async def handle_add(call: ServiceCall) -> None:
        name = call.data[ATTR_NAME].strip()

        def add(current: list[str]) -> list[str]:
            return [*current, name]

        await _update_favorites(add)

    async def handle_remove(call: ServiceCall) -> None:
        name = call.data[ATTR_NAME].strip().casefold()

        def remove(current: list[str]) -> list[str]:
            return [item for item in current if item.casefold() != name]

        await _update_favorites(remove)

    async def handle_set(call: ServiceCall) -> None:
        names = call.data[ATTR_NAMES_SERVICE]

        def replace(_: list[str]) -> list[str]:
            return list(names)

        await _update_favorites(replace)

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_FAVORITE, handle_add, schema=SERVICE_NAME_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_FAVORITE, handle_remove, schema=SERVICE_NAME_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_FAVORITES, handle_set, schema=SERVICE_NAMES_SCHEMA
    )
    domain_data[_SERVICES_REGISTERED] = True


@callback
def async_unload_services(hass: HomeAssistant) -> None:
    """Remove services when the last entry unloads."""
    if hass.data.get(DOMAIN, {}).get(_SERVICES_REGISTERED):
        hass.services.async_remove(DOMAIN, SERVICE_ADD_FAVORITE)
        hass.services.async_remove(DOMAIN, SERVICE_REMOVE_FAVORITE)
        hass.services.async_remove(DOMAIN, SERVICE_SET_FAVORITES)
        hass.data[DOMAIN][_SERVICES_REGISTERED] = False
