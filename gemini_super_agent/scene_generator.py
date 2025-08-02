import logging
from typing import Dict, Any, List
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID, SERVICE_TURN_ON, SERVICE_TURN_OFF,
    ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ATTR_TEMP
)
from .const import EVENT_SCENE_CREATED

_LOGGER = logging.getLogger(__name__)

async def generate_scene(
    agent: Any,
    name: str,
    description: str,
    entities: List[str] = None
) -> str:
    """Generate a dynamic scene based on description."""
    hass = agent.hass
    
    # If no entities specified, find relevant ones based on description
    if not entities:
        entities = await _find_entities_for_scene(agent, description)
    
    if not entities:
        return "No entities found for this scene."
    
    # Generate scene configuration based on description
    scene_config = await _generate_scene_config(agent, name, description, entities)
    
    try:
        # Create scene
        await hass.services.async_call(
            "scene",
            "create",
            scene_config
        )
        
        # Fire event
        hass.bus.async_fire(
            EVENT_SCENE_CREATED,
            {"name": name, "config": scene_config}
        )
        
        return f"Scene '{name}' created successfully with {len(entities)} entities."
    
    except Exception as e:
        return f"Error creating scene: {str(e)}"

async def _find_entities_for_scene(agent: Any, description: str) -> List[str]:
    """Find entities relevant to the scene description."""
    hass = agent.hass
    relevant_entities = []
    
    # Simple keyword matching (in a real implementation, this would be more sophisticated)
    description_lower = description.lower()
    
    # Light-related keywords
    if any(keyword in description_lower for keyword in ["light", "bright", "dim", "color"]):
        for entity_id, entity in agent.entities.items():
            if entity.get("domain") == "light":
                relevant_entities.append(entity_id)
    
    # Climate-related keywords
    if any(keyword in description_lower for keyword in ["temperature", "warm", "cool", "heat"]):
        for entity_id, entity in agent.entities.items():
            if entity.get("domain") == "climate":
                relevant_entities.append(entity_id)
    
    # Media-related keywords
    if any(keyword in description_lower for keyword in ["music", "sound", "tv", "movie"]):
        for entity_id, entity in agent.entities.items():
            if entity.get("domain") == "media_player":
                relevant_entities.append(entity_id)
    
    # Cover-related keywords
    if any(keyword in description_lower for keyword in ["blind", "curtain", "shade", "cover"]):
        for entity_id, entity in agent.entities.items():
            if entity.get("domain") == "cover":
                relevant_entities.append(entity_id)
    
    return relevant_entities[:10]  # Limit to 10 entities to avoid overly complex scenes

async def _generate_scene_config(
    agent: Any,
    name: str,
    description: str,
    entities: List[str]
) -> Dict[str, Any]:
    """Generate scene configuration based on description."""
    hass = agent.hass
    scene_config = {
        "scene_id": name.lower().replace(" ", "_"),
        "name": name,
        "entities": {},
    }
    
    description_lower = description.lower()
    
    for entity_id in entities:
        domain = entity_id.split(".")[0]
        state_obj = hass.states.get(entity_id)
        
        if not state_obj:
            continue
        
        # Default to current state
        scene_config["entities"][entity_id] = dict(state_obj.attributes)
        scene_config["entities"][entity_id]["state"] = state_obj.state
        
        # Adjust based on description keywords
        if domain == "light":
            if "bright" in description_lower:
                scene_config["entities"][entity_id]["brightness"] = 255
            elif "dim" in description_lower:
                scene_config["entities"][entity_id]["brightness"] = 100
            
            if "warm" in description_lower:
                scene_config["entities"][entity_id]["color_temp"] = 3000
            elif "cool" in description_lower:
                scene_config["entities"][entity_id]["color_temp"] = 5000
            
            if "red" in description_lower:
                scene_config["entities"][entity_id]["rgb_color"] = [255, 0, 0]
            elif "blue" in description_lower:
                scene_config["entities"][entity_id]["rgb_color"] = [0, 0, 255]
            elif "green" in description_lower:
                scene_config["entities"][entity_id]["rgb_color"] = [0, 255, 0]
        
        elif domain == "climate":
            if "warm" in description_lower:
                scene_config["entities"][entity_id]["temperature"] = 22.0
            elif "cool" in description_lower:
                scene_config["entities"][entity_id]["temperature"] = 18.0
        
        elif domain == "media_player":
            if "music" in description_lower:
                scene_config["entities"][entity_id]["media_content_type"] = "music"
            elif "tv" in description_lower:
                scene_config["entities"][entity_id]["media_content_type"] = "tvshow"
        
        elif domain == "cover":
            if "open" in description_lower:
                scene_config["entities"][entity_id]["state"] = "open"
            elif "close" in description_lower:
                scene_config["entities"][entity_id]["state"] = "closed"
    
    return scene_config