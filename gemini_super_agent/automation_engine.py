import logging
import yaml
from typing import Dict, List, Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.components import automation
from homeassistant.const import CONF_PLATFORM, CONF_ENTITY_ID, CONF_SERVICE
from .const import EVENT_AUTOMATION_CREATED

_LOGGER = logging.getLogger(__name__)

async def create_automation(
    agent: Any,
    name: str,
    triggers: List[Dict[str, Any]],
    actions: List[Dict[str, Any]],
    conditions: List[Dict[str, Any]] = None,
    description: str = None
) -> str:
    """Create a new Home Assistant automation."""
    hass = agent.hass
    
    # Build automation config
    automation_config = {
        "alias": name,
        "description": description or f"Created by Gemini Super Agent: {name}",
        "trigger": triggers,
        "action": actions,
    }
    
    if conditions:
        automation_config["condition"] = conditions
    
    try:
        # Validate config
        validated_config = cv.CONFIG_SCHEMA({automation.DOMAIN: automation_config})
        
        # Create automation
        await automation.async_create(validated_config[automation.DOMAIN])
        
        # Fire event
        hass.bus.async_fire(
            EVENT_AUTOMATION_CREATED,
            {"name": name, "config": automation_config}
        )
        
        return f"Automation '{name}' created successfully!"
    
    except Exception as e:
        _LOGGER.error(f"Error creating automation: {str(e)}")
        return f"Error creating automation: {str(e)}"