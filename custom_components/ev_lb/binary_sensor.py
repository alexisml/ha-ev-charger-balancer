"""Binary sensor platform for EV Charger Load Balancing."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EV LB binary sensor entities from a config entry."""
    async_add_entities([EvLbActiveBinarySensor(entry)])


class EvLbActiveBinarySensor(BinarySensorEntity):
    """Binary sensor indicating whether load balancing is actively controlling the charger."""

    _attr_has_entity_name = True
    _attr_translation_key = "active"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_is_on = False

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialise the binary sensor."""
        self._attr_unique_id = f"{entry.entry_id}_active"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="EV Charger Load Balancer",
            manufacturer="ev_lb",
            model="Virtual Load Balancer",
            entry_type=None,
        )
