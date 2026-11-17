"""
[harness] NOT FROM THE DOCS — the app this repo serves (`uv run --env-file .env
harness_app.py`). It is the Agno Quickstart's AgentOS `app` (main.py, verbatim
and unchanged) plus one more AGUI endpoint, added at the user's request (a
route with the tool agent, not a separate server):

- Tool Rendering publishes src/agents/main.py, whose `get_weather` tool is what
  the page renders. The file can't be imported (it imports an unpublished
  `tools` module), so this module compiles only the `get_weather` function
  from it, unchanged, with the names it uses: `json`, `tool`, and
  `get_weather_impl`. `get_weather_impl` lives in the unpublished `tools`
  module, so it is a STAND-IN below (user's choice) returning fixed sample
  weather.
- The tool agent uses the Quickstart agent's model, description and
  instructions, adding only `tools=[get_weather]`, and is mounted on the same
  app with Agno's AGUI interface under the /tool-rendering prefix (so its run
  endpoint is POST /tool-rendering/agui).

The `__main__` block mirrors the Quickstart's port (8000).
"""
import ast
import json
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os.interfaces.agui import AGUI
from agno.tools import tool

from main import agent, app


def get_weather_impl(location: str) -> dict:
    """[harness] STAND-IN — NOT FROM THE DOCS. The page's get_weather calls
    get_weather_impl from the `tools` module, which no page publishes. Fixed
    sample data, no network, so the rendered card has a result to show."""
    return {
        "location": location,
        "temperature": 22,
        "conditions": "Sunny",
        "humidity": 40,
        "note": "harness stand-in data",
    }


def _published_function(path: Path, name: str, namespace: dict):
    """Compile one top-level function from a published file, unchanged."""
    tree = ast.parse(path.read_text(), str(path))
    (node,) = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), namespace)
    return namespace[name]


get_weather = _published_function(
    Path(__file__).parent / "src" / "agents" / "main.py",
    "get_weather",
    {"json": json, "tool": tool, "get_weather_impl": get_weather_impl},
)

# [harness] The Quickstart agent's model, description and instructions, plus the page's tool.
tool_rendering_agent = Agent(
    model=OpenAIChat(reasoning_effort="none", id="gpt-6-luna"),
    description=agent.description,
    instructions=agent.instructions,
    tools=[get_weather],
)

app.include_router(AGUI(agent=tool_rendering_agent, prefix="/tool-rendering").get_router())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
