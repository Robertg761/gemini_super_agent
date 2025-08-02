{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import logging\
from homeassistant.core import HomeAssistant\
from homeassistant.config_entries import ConfigEntry\
from .const import DOMAIN, SERVICE_PROCESS_REQUEST\
from .gemini_agent import GeminiAgent\
\
_LOGGER = logging.getLogger(__name__)\
\
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:\
    """Set up Gemini Super Agent from a config entry."""\
    hass.data.setdefault(DOMAIN, \{\})\
    \
    agent = GeminiAgent(hass, entry.data)\
    hass.data[DOMAIN][entry.entry_id] = agent\
    \
    # Register service\
    async def async_process_request(call):\
        """Process a natural language request."""\
        user_input = call.data.get("text", "")\
        conversation_id = call.data.get("conversation_id", "default")\
        response = await agent.process_request(user_input, conversation_id)\
        \
        # Fire event with response\
        hass.bus.async_fire(\
            "gemini_super_agent_response",\
            \{\
                "response": response,\
                "conversation_id": conversation_id\
            \}\
        )\
    \
    hass.services.async_register(\
        DOMAIN, \
        SERVICE_PROCESS_REQUEST, \
        async_process_request\
    )\
    \
    return True\
\
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:\
    """Unload a config entry."""\
    hass.services.async_remove(DOMAIN, SERVICE_PROCESS_REQUEST)\
    hass.data[DOMAIN].pop(entry.entry_id)\
    return True}