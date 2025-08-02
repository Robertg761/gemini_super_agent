from typing import Dict, Any
from .automation_engine import create_automation
from .troubleshooter import analyze_logs, check_configuration
from .entity_manager import (
    find_entities, get_entity_state, control_entity,
    create_group, create_scene
)
from .scene_generator import generate_scene

# Function schemas for Gemini
FUNCTION_SCHEMAS = [
    {
        "name": "create_automation",
        "description": "Create a new Home Assistant automation",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the automation"},
                "description": {"type": "string", "description": "Description of what the automation does"},
                "triggers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string"},
                            "entity_id": {"type": "string"},
                            "event_type": {"type": "string"},
                            "event_data": {"type": "object"},
                        },
                    },
                },
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "condition": {"type": "string"},
                            "entity_id": {"type": "string"},
                            "state": {"type": "string"},
                        },
                    },
                },
                "actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "string"},
                            "entity_id": {"type": "string"},
                            "data": {"type": "object"},
                        },
                    },
                },
            },
            "required": ["name", "triggers", "actions"],
        },
    },
    {
        "name": "analyze_logs",
        "description": "Analyze Home Assistant logs for errors and warnings",
        "parameters": {
            "type": "object",
            "properties": {
                "timeframe": {
                    "type": "string",
                    "enum": ["1h", "6h", "12h", "24h", "7d"],
                    "description": "Timeframe to analyze logs"
                },
                "entity_id": {
                    "type": "string",
                    "description": "Specific entity to focus on (optional)"
                },
            },
        },
    },
    {
        "name": "check_configuration",
        "description": "Check Home Assistant configuration for errors",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "find_entities",
        "description": "Find entities based on criteria",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Partial name match"},
                "domain": {"type": "string", "description": "Entity domain (e.g., light, switch)"},
                "area": {"type": "string", "description": "Area name"},
                "device": {"type": "string", "description": "Device name"},
            },
        },
    },
    {
        "name": "get_entity_state",
        "description": "Get the current state of an entity",
        "parameters": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Entity ID"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "control_entity",
        "description": "Control an entity (turn on/off, set value, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Entity ID"},
                "action": {"type": "string", "enum": ["turn_on", "turn_off", "toggle", "set_value"]},
                "value": {"type": "string", "description": "Value to set (for set_value action)"},
            },
            "required": ["entity_id", "action"],
        },
    },
    {
        "name": "create_group",
        "description": "Create a new group of entities",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the group"},
                "entities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of entity IDs"
                },
                "icon": {"type": "string", "description": "Icon for the group (optional)"},
            },
            "required": ["name", "entities"],
        },
    },
    {
        "name": "generate_scene",
        "description": "Generate a dynamic scene based on description",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the scene"},
                "description": {"type": "string", "description": "Description of the scene/mood"},
                "entities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of entity IDs to include (optional)"
                },
            },
            "required": ["name", "description"],
        },
    },
]

# Function handlers
FUNCTION_HANDLERS = {
    "create_automation": create_automation,
    "analyze_logs": analyze_logs,
    "check_configuration": check_configuration,
    "find_entities": find_entities,
    "get_entity_state": get_entity_state,
    "control_entity": control_entity,
    "create_group": create_group,
    "generate_scene": generate_scene,
}