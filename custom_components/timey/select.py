"""Select platform for Timey (timer mode, screen rotation)."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import API_CONFIG, DOMAIN
from .coordinator import TimeyCoordinator
from .entity import TimeyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Timey select entities."""
    coordinator: TimeyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TimeyTimerModeSelect(coordinator),
        TimeyRotationSelect(coordinator),
    ])


class TimeyTimerModeSelect(TimeyEntity, SelectEntity):
    """Select entity for timer display mode."""

    _attr_name = "Display mode"
    _attr_icon = "mdi:clock-outline"
    _attr_options = ["Countdown", "Departure times"]

    _MODE_MAP = {0: "Countdown", 1: "Departure times"}
    _REVERSE_MAP = {"Countdown": 0, "Departure times": 1}

    def __init__(self, coordinator: TimeyCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_unique_id = f"{chip_id}_timer_mode"

    @property
    def current_option(self) -> str | None:
        """Return the current timer mode."""
        mode = self.coordinator.data.get("timer_mode", 0)
        return self._MODE_MAP.get(mode, "Countdown")

    async def async_select_option(self, option: str) -> None:
        """Set the timer mode."""
        value = self._REVERSE_MAP.get(option, 0)
        await self.coordinator.async_post(API_CONFIG, {"timer_mode": value})


class TimeyRotationSelect(TimeyEntity, SelectEntity):
    """Select entity for screen rotation."""

    _attr_name = "Screen rotation"
    _attr_icon = "mdi:screen-rotation"
    _attr_options = ["Normal", "Flipped"]

    _ROT_MAP = {1: "Normal", 3: "Flipped"}
    _REVERSE_MAP = {"Normal": 1, "Flipped": 3}

    def __init__(self, coordinator: TimeyCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_unique_id = f"{chip_id}_screen_rotation"

    @property
    def current_option(self) -> str | None:
        """Return the current rotation."""
        rot = self.coordinator.data.get("screen_rotation", 1)
        return self._ROT_MAP.get(rot, "Normal")

    async def async_select_option(self, option: str) -> None:
        """Set the screen rotation."""
        value = self._REVERSE_MAP.get(option, 1)
        await self.coordinator.async_post(API_CONFIG, {"screen_rotation": value})
