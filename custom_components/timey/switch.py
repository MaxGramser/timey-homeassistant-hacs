"""Switch platform for Timey (smart departure, schedule)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up Timey switch entities."""
    coordinator: TimeyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TimeySmartDepartureSwitch(coordinator),
        TimeyScheduleSwitch(coordinator),
    ])


class TimeySmartDepartureSwitch(TimeyEntity, SwitchEntity):
    """Switch for smart departure mode (first reachable vs all upcoming)."""

    _attr_name = "Smart departure"
    _attr_icon = "mdi:run-fast"

    def __init__(self, coordinator: TimeyCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_unique_id = f"{chip_id}_smart_departure"

    @property
    def is_on(self) -> bool:
        """Return true if smart departure is enabled."""
        return self.coordinator.data.get("smart_departure", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable smart departure."""
        await self.coordinator.async_post(API_CONFIG, {"smart_departure": True})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable smart departure."""
        await self.coordinator.async_post(API_CONFIG, {"smart_departure": False})


class TimeyScheduleSwitch(TimeyEntity, SwitchEntity):
    """Switch for schedule mode.

    When schedule is ON, the device follows its configured daily schedule
    and the display light cannot be manually turned on/off.
    When schedule is OFF, the display can be controlled manually via the light entity.
    """

    _attr_name = "Schedule"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: TimeyCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_unique_id = f"{chip_id}_schedule_enabled"

    @property
    def is_on(self) -> bool:
        """Return true if schedule is enabled."""
        return self.coordinator.data.get("schedule_enabled", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes with schedule info."""
        return {
            "info": "When enabled, the display follows the configured schedule and cannot be manually turned on/off.",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable schedule."""
        await self.coordinator.async_post(API_CONFIG, {"schedule_enabled": True})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable schedule. The display can now be controlled manually."""
        await self.coordinator.async_post(API_CONFIG, {"schedule_enabled": False})
