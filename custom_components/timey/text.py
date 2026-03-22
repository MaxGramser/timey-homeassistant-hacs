"""Text platform for Timey (TPC code configuration)."""

from __future__ import annotations

import logging

from homeassistant.components.text import TextEntity
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
    """Set up Timey text entities."""
    coordinator: TimeyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TimeyTpcText(coordinator, "tpc1", "Stop code 1"),
        TimeyTpcText(coordinator, "tpc2", "Stop code 2"),
    ])


class TimeyTpcText(TimeyEntity, TextEntity):
    """Text entity for a Timey TPC code."""

    _attr_native_max = 40

    def __init__(self, coordinator: TimeyCoordinator, key: str, name: str) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_unique_id = f"{chip_id}_{key}"

    @property
    def native_value(self) -> str | None:
        """Return the current TPC value."""
        return self.coordinator.data.get(self._key, "")

    async def async_set_value(self, value: str) -> None:
        """Set a new TPC value."""
        await self.coordinator.async_post(API_CONFIG, {self._key: value})
