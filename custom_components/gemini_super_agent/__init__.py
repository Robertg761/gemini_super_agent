import logging
import aiohttp
import yaml

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gemini_super_agent"
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key="

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Gemini Super Agent component."""

    async def handle_prompt(call: ServiceCall):
        """Handle the service call to generate content with Gemini."""
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


    hass.services.async_register(DOMAIN, "prompt", handle_prompt)
    _LOGGER.info("Gemini Super Agent is set up and ready.")
    
    return True
