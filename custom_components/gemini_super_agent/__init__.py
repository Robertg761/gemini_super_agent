import logging
import aiohttp
import yaml

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gemini_super_agent"
# Updated to use the latest and best model as suggested.
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key="

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gemini Super Agent from a config entry."""

    async def handle_prompt(call: ServiceCall):
        """Handle the service call to generate content with Gemini."""
        # Note: In a real config flow, the API key would be stored in the entry.data
        # and retrieved here instead of being passed in the service call.
        # For now, we'll keep the service call structure for simplicity.
        api_key = call.data.get("api_key")
        prompt = call.data.get("prompt")

        if not api_key or not prompt:
            _LOGGER.error("API key and prompt are required.")
            return

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        full_url = f"{GEMINI_API_ENDPOINT}{api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(full_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Process the result from Gemini
                        _LOGGER.info("Received response from Gemini.")
                        
                        # Example of extracting the text
                        try:
                            text_response = result['candidates'][0]['content']['parts'][0]['text']
                            _LOGGER.info(f"Gemini Response: {text_response}")
                            
                            # You can fire an event with the response
                            hass.bus.async_fire(f"{DOMAIN}_response", {"response_text": text_response})

                        except (KeyError, IndexError) as e:
                            _LOGGER.error(f"Error parsing Gemini response: {e}")
                            _LOGGER.error(f"Full response: {result}")

                    else:
                        _LOGGER.error(f"Error calling Gemini API: {response.status} - {await response.text()}")

        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error calling Gemini API: {e}")

    # Register the service
    hass.services.async_register(DOMAIN, "prompt", handle_prompt)
    _LOGGER.info("Gemini Super Agent service is registered.")
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when the integration is removed or reloaded.
    # We remove the service that was registered.
    hass.services.async_remove(DOMAIN, "prompt")
    _LOGGER.info("Gemini Super Agent service unregistered.")
    return True
