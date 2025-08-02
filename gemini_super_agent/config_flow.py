import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_API_KEY, CONF_MODEL, DEFAULT_MODEL

class GeminiSuperAgentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input[CONF_API_KEY]:
                errors[CONF_API_KEY] = "api_key_empty"
            else:
                return self.async_create_entry(
                    title="Gemini Super Agent",
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): vol.In([
                    "gemini-pro", "gemini-pro-vision"
                ]),
            }),
            errors=errors,
        )