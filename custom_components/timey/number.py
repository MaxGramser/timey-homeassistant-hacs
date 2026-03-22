"""Number platform for Timey (TTM configuration)."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import API_CONFIG, DOMAIN
from .coordinator import TimeyCoordinator
from .entity import TimeyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Timey number entities."""
    coordinator: TimeyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TimeyTtmNumber(coordinator, "ttm1", "Walk time stop 1"),
        TimeyTtmNumber(coordinator, "ttm2", "Walk time stop 2"),
    ])


class TimeyTtmNumber(TimeyEntity, NumberEntity):
    """Number entity for time-to-make-it (walking time to stop)."""

    _attr_native_min_value = 0
    _attr_native_max_value = 3600
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:walk"

    def __init__(self, coordinator: TimeyCoordinator, key: str, name: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_unique_id = f"{chip_id}_{key}"

    @property
    def native_value(self) -> float | None:
        """Return the current TTM value in seconds."""
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        """Set a new TTM value."""
        await self.coordinator.async_post(API_CONFIG, {self._key: int(value)})
