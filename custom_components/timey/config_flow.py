"""Config flow for Timey integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import API_STATE, CONF_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _validate_host(host: str) -> dict:
    """Validate that we can connect to the device and return its state."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://{host}{API_STATE}", timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


class TimeyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Timey."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._chip_id: str | None = None
        self._name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual setup by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                data = await _validate_host(host)
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                chip_id = data.get("chip_id", host)
                await self.async_set_unique_id(chip_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=f"Timey {chip_id[-4:]}",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle Zeroconf discovery."""
        host = discovery_info.host
        properties = discovery_info.properties

        chip_id = properties.get("chip_id", host)
        await self.async_set_unique_id(chip_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._host = host
        self._chip_id = chip_id
        self._name = f"Timey {chip_id[-4:]}"

        self.context["title_placeholders"] = {"name": self._name}

        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm Zeroconf discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._name or "Timey",
                data={CONF_HOST: self._host},
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": self._name, "host": self._host},
        )
