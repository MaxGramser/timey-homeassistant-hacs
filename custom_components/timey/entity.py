"""Base entity for Timey devices."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TimeyCoordinator


class TimeyEntity(CoordinatorEntity[TimeyCoordinator]):
    """Base entity for a Timey device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TimeyCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        chip_id = coordinator.data.get("chip_id", "unknown")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, chip_id)},
            name=f"Timey {chip_id[-4:]}",
            manufacturer="Timey Club",
            model=coordinator.data.get("model", "T-Display-S3"),
            sw_version=coordinator.data.get("firmware", "unknown"),
            configuration_url=f"http://{coordinator.host}",
        )
