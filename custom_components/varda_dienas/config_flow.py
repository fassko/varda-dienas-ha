"""Config flow for Vārda dienas."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_FAVORITES,
    CONF_SHOW_EXTENDED,
    DEFAULT_FAVORITES,
    DEFAULT_SHOW_EXTENDED,
    DOMAIN,
)
from .repository import NameDayRepository


def _parse_favorites(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        raw = value
    else:
        raw = str(value).replace(";", ",").split(",")
    return NameDayRepository().normalize_favorites([str(item) for item in raw])


def _favorites_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_SHOW_EXTENDED,
                default=defaults.get(CONF_SHOW_EXTENDED, DEFAULT_SHOW_EXTENDED),
            ): bool,
            vol.Optional(
                CONF_FAVORITES,
                default=", ".join(
                    defaults.get(CONF_FAVORITES, DEFAULT_FAVORITES) or []
                ),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    multiline=True,
                    type=selector.TextSelectorType.TEXT,
                )
            ),
        }
    )


class VardaDienasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vārda dienas."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the single shared config entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            favorites = _parse_favorites(user_input.get(CONF_FAVORITES))
            return self.async_create_entry(
                title="Vārda dienas",
                data={},
                options={
                    CONF_SHOW_EXTENDED: bool(
                        user_input.get(CONF_SHOW_EXTENDED, DEFAULT_SHOW_EXTENDED)
                    ),
                    CONF_FAVORITES: favorites,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_favorites_schema(
                {
                    CONF_SHOW_EXTENDED: DEFAULT_SHOW_EXTENDED,
                    CONF_FAVORITES: DEFAULT_FAVORITES,
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return VardaDienasOptionsFlow()


class VardaDienasOptionsFlow(OptionsFlow):
    """Configure favorites and extended names."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            favorites = _parse_favorites(user_input.get(CONF_FAVORITES))
            return self.async_create_entry(
                title="",
                data={
                    CONF_SHOW_EXTENDED: bool(
                        user_input.get(CONF_SHOW_EXTENDED, DEFAULT_SHOW_EXTENDED)
                    ),
                    CONF_FAVORITES: favorites,
                },
            )

        current = {
            CONF_SHOW_EXTENDED: self.config_entry.options.get(
                CONF_SHOW_EXTENDED, DEFAULT_SHOW_EXTENDED
            ),
            CONF_FAVORITES: self.config_entry.options.get(
                CONF_FAVORITES, DEFAULT_FAVORITES
            ),
        }
        return self.async_show_form(
            step_id="init",
            data_schema=_favorites_schema(current),
        )
