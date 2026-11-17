import { CopilotRuntime } from "@copilotkit/runtime/v2";

import { toolRenderingAgent } from "../agents";

/**
 * [harness] The runtime behind /generative-ui/tool-rendering, mounted at
 * /api/copilotkit-tool-rendering on the same Node server (user's choice: its
 * own runtime path, not a separate server).
 *
 * Tool Rendering's samples use agent `default`, which every other route shares
 * with the Quickstart agent. Here `default` is the tool agent that
 * agent/harness_app.py mounts at /tool-rendering: the Quickstart's model plus
 * the page's published `get_weather` (with a flagged `get_weather_impl`
 * stand-in). The three Tool Rendering App.vue files point their runtime-url
 * here (labelled). README §9.
 */
export function createToolRenderingRuntime(): CopilotRuntime {
  return new CopilotRuntime({ agents: { default: toolRenderingAgent() } });
}
