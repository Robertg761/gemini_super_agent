{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import logging\
import re\
from typing import Dict, Any, List\
from homeassistant.core import HomeAssistant\
from homeassistant.helpers import system_info\
from homeassistant.components.websocket_api import async_register_command\
\
_LOGGER = logging.getLogger(__name__)\
\
async def analyze_logs(\
    agent: Any,\
    timeframe: str = "24h",\
    entity_id: str = None\
) -> str:\
    """Analyze Home Assistant logs for errors and warnings."""\
    hass = agent.hass\
    \
    # Get logs (this is a simplified version)\
    # In a real implementation, you would fetch logs from the recorder or log files\
    logs = await hass.async_add_executor_job(\
        lambda: hass.data.get("logger", \{\}).get("logs", [])\
    )\
    \
    # Filter logs by timeframe and entity\
    filtered_logs = []\
    for log in logs:\
        if entity_id and entity_id not in log.get("message", ""):\
            continue\
        # Add timeframe filtering logic here\
        filtered_logs.append(log)\
    \
    # Analyze logs for errors and warnings\
    errors = []\
    warnings = []\
    \
    for log in filtered_logs:\
        message = log.get("message", "")\
        if "ERROR" in message:\
            errors.append(message)\
        elif "WARNING" in message:\
            warnings.append(message)\
    \
    # Generate summary\
    result = f"Found \{len(errors)\} errors and \{len(warnings)\} warnings in the last \{timeframe\}.\\n\\n"\
    \
    if errors:\
        result += "Errors:\\n"\
        for i, error in enumerate(errors[:5], 1):  # Limit to first 5 errors\
            result += f"\{i\}. \{error\}\\n"\
    \
    if warnings:\
        result += "\\nWarnings:\\n"\
        for i, warning in enumerate(warnings[:5], 1):  # Limit to first 5 warnings\
            result += f"\{i\}. \{warning\}\\n"\
    \
    if not errors and not warnings:\
        result += "No errors or warnings found in the specified timeframe."\
    \
    return result\
\
async def check_configuration(agent: Any) -> str:\
    """Check Home Assistant configuration for errors."""\
    hass = agent.hass\
    \
    # Get system info\
    sys_info = await system_info.async_get_system_info(hass)\
    \
    # Check configuration.yaml for syntax errors\
    try:\
        with open(hass.config.path("configuration.yaml"), "r") as f:\
            config_content = f.read()\
        \
        # Try to parse as YAML\
        yaml.safe_load(config_content)\
        config_status = "Configuration.yaml is valid."\
    except Exception as e:\
        config_status = f"Error in configuration.yaml: \{str(e)\}"\
    \
    # Check for common issues\
    issues = []\
    \
    # Check for missing integrations\
    if "default_config" not in hass.config.components:\
        issues.append("default_config integration is not enabled")\
    \
    # Check for recorder issues\
    if "recorder" in hass.config.components:\
        recorder_history = hass.states.get("sensor.recorder_issues")\
        if recorder_history and recorder_history.state != "0":\
            issues.append(f"Recorder has \{recorder_history.state\} issues")\
    \
    result = config_status + "\\n\\n"\
    \
    if issues:\
        result += "Potential issues found:\\n"\
        for i, issue in enumerate(issues, 1):\
            result += f"\{i\}. \{issue\}\\n"\
    else:\
        result += "No common configuration issues detected."\
    \
    return result}