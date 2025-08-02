import logging
from typing import Dict, Any, List
from homeassistant.core import HomeAssistant, State
from homeassistant.const import (
    ATTR_ENTITY_ID, SERVICE_TURN_ON, SERVICE_TURN_OFF,
    SERVICE_TOGGLE, ATTR_DOMAIN
)
from homeassistant.helpers import entity_registry as er
from .const import EVENT_SCENE_CREATED

_LOGGER = logging.getLogger(__name__)

async def find_entities(
    agent: Any,
    name: str = None,
    domain: str = None,
    area: str = None,
    device: str = None
) -> str:
    """Find entities based on criteria."""
    hass = agent.hass
    matches = []
    
    for entity_id, entity in agent.entities.items():
        # Check name match
        if name and name.lower() not in entity.get("name", "").lower():
            continue
        
        # Check domain match
        if domain and entity.get("domain") != domain:
            continue
        
        # Check area match
        if area:
            area_id = entity.get("area_id")
            if area_id:
                area_info = agent.areas.get(area_id, {})
                if area.lower() not in area_info.get("name", "").lower():
                    continue
            else:
                continue
        
        # Check device match
        if device:
            device_id = entity.get("device_id")
            if device_id:
                device_info = agent.devices.get(device_id, {})
                if device.lower() not in device_info.get("name", "").lower():
                    continue
            else:
                continue
        
        matches.append(f"{entity_id}: {entity.get('name', 'Unnamed')}")
    
    if not matches:
        return "No entities found matching your criteria."
    
    result = f"Found {len(matches)} matching entities:\n"
    for i, match in enumerate(matches, 1):
        result += f"{i}. {match}\n"
    
    return result

async def get_entity_state(agent: Any, entity_id: str) -> str:
    """Get the current state of an entity."""
    hass = agent.hass
    state_obj = hass.states.get(entity_id)
    
    if not state_obj:
        return f"Entity {entity_id} not found."
    
    result = f"Entity: {entity_id}\n"
    result += f"State: {state_obj.state}\n"
    
    if state_obj.attributes:
        result += "Attributes:\n"
        for key, value in state_obj.attributes.items():
            result += f"  {key}: {value}\n"
    
    return result

async def control_entity(
    agent: Any,
    entity_id: str,
    action: str,
    value: str = None
) -> str:
    """Control an entity (turn on/off, set value, etc.)."""
    hass = agent.hass
    
    # Validate entity exists
    if entity_id not in agent.entities:
        return f"Entity {entity_id} not found."
    
    # Get domain
    domain = entity_id.split(".")[0]
    
    try:
        if action == "turn_on":
            await hass.services.async_call(domain, SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id})
            return f"Turned on {entity_id}."
        
        elif action == "turn_off":
            await hass.services.async_call(domain, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id})
            return f"Turned off {entity_id}."
        
        elif action == "toggle":
            await hass.services.async_call(domain, SERVICE_TOGGLE, {ATTR_ENTITY_ID: entity_id})
            return f"Toggled {entity_id}."
        
        elif action == "set_value" and value:
            # This is domain-specific, so we'll handle common cases
            if domain == "light":
                await hass.services.async_call(
                    domain,
                    "turn_on",
                    {ATTR_ENTITY_ID: entity_id, "brightness": int(value)}
                )
                return f"Set brightness of {entity_id} to {value}."
            
            elif domain == "climate":
                await hass.services.async_call(
                    domain,
                    "set_temperature",
                    {ATTR_ENTITY_ID: entity_id, "temperature": float(value)}
                )
                return f"Set temperature of {entity_id} to {value}."
            
            elif domain == "media_player":
                await hass.services.async_call(
                    domain,
                    "volume_set",
                    {ATTR_ENTITY_ID: entity_id, "volume_level": float(value)}
                )
                return f"Set volume of {entity_id} to {value}."
            
            else:
                return f"Setting values not supported for domain {domain}."
        
        else:
            return f"Unsupported action: {action}."
    
    except Exception as e:
        return f"Error controlling {entity_id}: {str(e)}"

async def create_group(
    agent: Any,
    name: str,
    entities: List[str],
    icon: str = None
) -> str:
    """Create a new group of entities."""
    hass = agent.hass
    
    # Validate entities exist
    invalid_entities = [e for e in entities if e not in agent.entities]
    if invalid_entities:
        return f"Invalid entities: {', '.join(invalid_entities)}"
    
    # Create group config
    group_config = {
        "name": name,
        "entities": entities,
    }
    
    if icon:
        group_config["icon"] = icon
    
    try:
        # Create group via service call
        await hass.services.async_call(
            "group",
            "set",
            {
                "object_id": name.lower().replace(" ", "_"),
                "name": name,
                "entities": entities,
                "icon": icon,
            }
        )
        
        return f"Group '{name}' created successfully with {len(entities)} entities."
    
    except Exception as e:
        return f"Error creating group: {str(e)}"

async def create_scene(
    agent: Any,
    name: str,
    entities: List[str],
    snapshot_entities: bool = True
) -> str:
    """Create a new scene."""
    hass = agent.hass
    
    # Validate entities exist
    invalid_entities = [e for e in entities if e not in agent.entities]
    if invalid_entities:
        return f"Invalid entities: {', '.join(invalid_entities)}"
    
    try:
        # Create scene via service call
        await hass.services.async_call(
            "scene",
            "create",
            {
                "scene_id": name.lower().replace(" ", "_"),
                "name": name,
                "entities": entities,
                "snapshot_entities": snapshot_entities,
            }
        )
        
        # Fire event
        hass.bus.async_fire(
            EVENT_SCENE_CREATED,
            {"name": name, "entities": entities}
        )
        
        return f"Scene '{name}' created successfully with {len(entities)} entities."
    
    except Exception as e:
        return f"Error creating scene: {str(e)}"