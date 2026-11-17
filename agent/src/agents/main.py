import json

from agno.agent.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from dotenv import load_dotenv
from tools import (
    RENDER_A2UI_TOOL_SCHEMA,
    build_a2ui_operations_from_tool_call,
    get_weather_impl,
    query_data_impl,
    schedule_meeting_impl,
    search_flights_impl,
)
from tools.types import Flight

load_dotenv()


@tool
def get_weather(location: str):
    """
    Get the weather for a given location. Ensure location is fully spelled out.

    Args:
        location (str): The location to get the weather for.

    Returns:
        str: Weather data as JSON.
    """
    return json.dumps(get_weather_impl(location))

