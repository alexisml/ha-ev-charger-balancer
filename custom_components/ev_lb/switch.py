"""Switch platform for EV Charger Load Balancing."""

from __future__ import annotations

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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
    """Set up EV LB switch entities from a config entry."""
    async_add_entities([EvLbEnabledSwitch(entry)])


class EvLbEnabledSwitch(SwitchEntity):
    """Switch to enable or disable dynamic load balancing."""

    _attr_has_entity_name = True
    _attr_translation_key = "enabled"
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_is_on = True

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialise the switch."""
        self._attr_unique_id = f"{entry.entry_id}_enabled"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="EV Charger Load Balancer",
            manufacturer="ev_lb",
            model="Virtual Load Balancer",
            entry_type=None,
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on load balancing."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off load balancing."""
        self._attr_is_on = False
        self.async_write_ha_state()
