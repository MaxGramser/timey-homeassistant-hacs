"""Data coordinator for Timey devices."""

from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_STATE, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TimeyCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that polls the Timey REST API."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = host
        self._base_url = f"http://{host}"

    async def _async_update_data(self) -> dict:
        """Fetch state from the device."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}{API_STATE}", timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with Timey device: {err}") from err

    async def async_post(self, endpoint: str, data: dict) -> dict | None:
        """Send a POST command to the device and return the response."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}{endpoint}",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 409:
                        body = await resp.json()
                        raise ScheduleActiveError(body.get("error", "Schedule is active"))
                    resp.raise_for_status()
                    result = await resp.json()
                    self.async_set_updated_data(result)
                    return result
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Timey device: {err}") from err


class ScheduleActiveError(Exception):
    """Raised when the device rejects a command because schedule is active."""
