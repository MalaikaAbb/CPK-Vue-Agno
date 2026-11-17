import { AgnoAgent } from "@ag-ui/agno";

/**
 * Agents for every runtime in this repo.
 *
 * `myAgent()` is the agent the Agno landing page registers
 * (https://docs.copilotkit.ai/vue/agno — its only code block), verbatim:
 * `new AgnoAgent({ url: "http://localhost:8000/agui" })` from `@ag-ui/agno`,
 * pointed at the Agno Quickstart's AgentOS app (agent/main.py: Agent +
 * OpenAIChat, AgentOS with the AGUI interface, served on :8000 at /agui).
 * The URL is hard-coded as published, so AGENT_URL is not read.
 *
 * [harness] Doc agent ids. The landing page registers only `my_agent`, while
 * the Vue samples use `default` (no agent-id) and ids no page registers. By the
 * user's rules a page's own published agent would run under its id if it were
 * complete — but neither Agno page backend can run as a whole: Tool Rendering's
 * src/agents/main.py imports an unpublished `tools` module, and Sub-agents'
 * src/agents/subagents.py builds no supervisor. So every id is the landing
 * page's my_agent, unchanged. Tool Rendering's `get_weather` alone runs on
 * agent/harness_app.py's /tool-rendering (with a flagged get_weather_impl
 * stand-in), reached through its own runtime path (toolRenderingAgent,
 * runtimes/tool-rendering.ts). The Generative UI › Components samples also use
 * `default` (the choice made for ms-agent-py, same rules).
 */
export function myAgent() {
  // Verbatim from the landing page's runtime route.
  return new AgnoAgent({ url: "http://localhost:8000/agui" });
}

/** [harness] The landing page's AgnoAgent, pointed at harness_app.py's /tool-rendering/agui (Tool Rendering's get_weather agent). */
export function toolRenderingAgent() {
  return new AgnoAgent({ url: "http://localhost:8000/tool-rendering/agui" });
}

/** Doc agent ids, and the page each one comes from. */
export const DOC_AGENT_IDS = {
  default: "no agent-id: Quickstart, Slots, Frontend Tools, Components as Tools, …",
  "my-agent": "Prebuilt Components, Headless UI, Headless Threads",
  sales: "Programmatic Control",
  support: "Threads Drawer",
  researcher: "State Rendering",
  workspace: "Shared State",
  writer: "State Streaming",
} as const;

export function docAgents() {
  return Object.fromEntries(Object.keys(DOC_AGENT_IDS).map((id) => [id, myAgent()]));
}
