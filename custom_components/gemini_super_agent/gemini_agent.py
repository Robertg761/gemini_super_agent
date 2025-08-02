import logging
import json
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import area_registry as ar
from .function_handlers import FUNCTION_HANDLERS, FUNCTION_SCHEMAS

_LOGGER = logging.getLogger(__name__)

class GeminiAgent:
    def __init__(self, hass: HomeAssistant, config_data: dict):
        self.hass = hass
        genai.configure(api_key=config_data["api_key"])
        self.model = genai.GenerativeModel(config_data.get("model", "gemini-pro"))
        self.chat_sessions = {}
        self.functions = FUNCTION_SCHEMAS
        self.function_handlers = FUNCTION_HANDLERS
        
        # Initialize registries
        self.entity_registry = er.async_get(hass)
        self.device_registry = dr.async_get(hass)
        self.area_registry = ar.async_get(hass)
        
        # Cache entities and devices
        self.entities = {}
        self.devices = {}
        self.areas = {}
        self._cache_registries()

    def _cache_registries(self):
        """Cache Home Assistant entities, devices, and areas."""
        # Cache entities
        for entity_id, entry in self.entity_registry.entities.items():
            self.entities[entity_id] = {
                "name": entry.name or entry.original_name,
                "device_id": entry.device_id,
                "area_id": entry.area_id,
                "entity_id": entity_id,
                "domain": entry.domain,
            }
        
        # Cache devices
        for device_id, entry in self.device_registry.devices.items():
            self.devices[device_id] = {
                "name": entry.name,
                "area_id": entry.area_id,
                "manufacturer": entry.manufacturer,
                "model": entry.model,
            }
        
        # Cache areas
        for area_id, entry in self.area_registry.areas.items():
            self.areas[area_id] = {
                "name": entry.name,
                "picture": entry.picture,
            }

    async def process_request(self, user_input: str, conversation_id: str = "default") -> str:
        """Process a natural language request from the user."""
        # Get or create chat session
        if conversation_id not in self.chat_sessions:
            self.chat_sessions[conversation_id] = self.model.start_chat(history=[])
        
        chat = self.chat_sessions[conversation_id]
        
        # Build context with Home Assistant state
        context = self._build_context()
        
        # Create prompt with context
        prompt = f"""
        You are a Home Assistant Super Agent with access to the following devices and entities:
        
        {context}
        
        User request: {user_input}
        
        Please help the user with their request. Use the available functions to interact with Home Assistant.
        """
        
        # Send message to Gemini
        response = await self.hass.async_add_executor_job(
            lambda: chat.send_message(
                prompt,
                tools=self.functions,
                tool_config={"function_calling_config": "ANY"}
            )
        )
        
        # Process function calls if any
        if response.function_calls:
            function_responses = []
            for function_call in response.function_calls:
                function_name = function_call.name
                function_args = function_call.args
                
                _LOGGER.info(f"Calling function: {function_name} with args: {function_args}")
                
                handler = self.function_handlers.get(function_name)
                if handler:
                    try:
                        result = await handler(self, **function_args)
                        function_responses.append(
                            {"name": function_name, "response": result}
                        )
                    except Exception as e:
                        _LOGGER.error(f"Error in function {function_name}: {str(e)}")
                        function_responses.append(
                            {"name": function_name, "error": str(e)}
                        )
                else:
                    function_responses.append(
                        {"name": function_name, "error": "Handler not found"}
                    )
            
            # Send function responses back to Gemini
            response = await self.hass.async_add_executor_job(
                lambda: chat.send_message(
                    [
                        {"function_response": fr}
                        for fr in function_responses
                    ]
                )
            )
        
        return response.text

    def _build_context(self) -> str:
        """Build context string with Home Assistant state."""
        context = "Entities:\n"
        
        # Add entities
        for entity_id, entity in self.entities.items():
            state = self.hass.states.get(entity_id)
            state_str = state.state if state else "unknown"
            context += f"- {entity_id}: {entity.get('name', 'Unnamed')} (State: {state_str})\n"
        
        # Add devices
        context += "\nDevices:\n"
        for device_id, device in self.devices.items():
            context += f"- {device_id}: {device.get('name', 'Unnamed')} ({device.get('manufacturer', 'Unknown')} {device.get('model', 'Model')})\n"
        
        # Add areas
        context += "\nAreas:\n"
        for area_id, area in self.areas.items():
            context += f"- {area_id}: {area.get('name', 'Unnamed')}\n"
        
        return context