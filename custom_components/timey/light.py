"""Light platform for Timey."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import API_LIGHT, DOMAIN
from .coordinator import ScheduleActiveError, TimeyCoordinator
from .entity import TimeyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Timey light."""
    coordinator: TimeyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TimeyLight(coordinator)])


class TimeyLight(TimeyEntity, LightEntity):
    """Represents the Timey display as a light.

    When the schedule is enabled, the display follows the configured daily
    schedule and cannot be turned on/off manually. Disable the schedule switch
    first to control the display manually.
    """

    _attr_name = "Display"
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, coordinator: TimeyCoordinator) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_unique_id = f"{chip_id}_light"

    @property
    def is_on(self) -> bool:
        """Return true if the display is on."""
        return self.coordinator.data.get("on", False)

    @property
    def brightness(self) -> int | None:
        """Return the brightness (0-255)."""
        pct = self.coordinator.data.get("brightness", 0)
        return round(pct * 255 / 100)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs: dict[str, Any] = {}
        if self.coordinator.data.get("schedule_enabled", False):
            attrs["notice"] = (
                "Schedule is active. Turn off the Schedule switch to control the display manually."
            )
        return attrs

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the display."""
        data: dict[str, Any] = {"on": True}
        if ATTR_BRIGHTNESS in kwargs:
            data["brightness"] = round(kwargs[ATTR_BRIGHTNESS] * 100 / 255)
        try:
            await self.coordinator.async_post(API_LIGHT, data)
        except ScheduleActiveError as err:
            raise HomeAssistantError(
                "Schedule is active. Turn off the Schedule switch first to control the display manually."
            ) from err

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the display."""
        try:
            await self.coordinator.async_post(API_LIGHT, {"on": False})
        except ScheduleActiveError as err:
            raise HomeAssistantError(
                "Schedule is active. Turn off the Schedule switch first to control the display manually."
            ) from err
