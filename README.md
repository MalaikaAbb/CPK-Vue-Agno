# CopilotKit Vue + Agno Test Suite

A navigable, working test harness for CopilotKit's **Vue** frontend against an **Agno** (Python) agent. Each Vue doc page is a route that runs that page's own code, plus the nine Generative UI › Components pages.

| | |
|---|---|
| **Doc sync date** | Machine-maintained: `doc-snapshot/manifest.json` → `syncedAt` (baseline taken 2026-11-13, 31 pages: 22 Vue pages + 9 Components pages). |
| **CopilotKit packages** | `@copilotkit/vue` 1.87.0 · `@copilotkit/core` 1.87.0 · `@copilotkit/runtime` 1.87.0 · `@ag-ui/agno` 0.0.6 (`AgnoAgent`, the landing page's agent client) |
| **Agno** | `agno` 3.2.0 · `fastapi` 0.163.1 · `uvicorn` 0.54.0 · `openai` 3.51.0 · `ag-ui-protocol` 1.0.0 · `python-multipart` 0.0.33 (harness-added, §9.2) · Python 3.14 (uv default; the Quickstart pins none) |
| **Frontend** | Vite 8.3 · Vue 3.5 · vue-router 5.5 · TypeScript 6.0 · Tailwind 4.3 (harness chrome only) · zod 3.25.76 · `chart.js` 4.6.1 · `maplibre-gl` 5.24.1 (Components page's install line) |
| **Build status** | No CI. `vite build` ✅. `vue-tsc` reports 9 errors, all in published doc code (§9.10). All 86 URLs (every route, demo and sample, including the nine Components routes) mounted in headless Chrome with **zero console or page errors**. The chain (runtime → `AgnoAgent` → Agno AgentOS agent → model call) was driven with the agent's `OPENAI_BASE_URL` pointed at a local capture server, so nothing left the machine: the captured request carried the run's frontend tool **and its context**. **No route has been driven against a live model yet.** |

---

## 2. Overview

Agno is a Python agent framework. CopilotKit reaches it over AG-UI: Agno's `AgentOS` serves an `Agent` with its `AGUI` interface (at `/agui`), the Copilot Runtime registers an `AgnoAgent` (`@ag-ui/agno`) pointed at it, and `@copilotkit/vue` renders the conversation, tools and generated UI.

This repo turns the Quickstart and the Basics, Generative UI, Interactivity and Agent capabilities sections of the Vue Agno sidebar (22 pages) into one navigable Vite app. It adds the nine **Generative UI › Components** pages, which are not under `/vue` and print each sample for React, Angular, React Native and Vue; only their Vue tab is used. Every route mounts the page's code verbatim, bugs included, and shows the exact files that run. Anything the harness added is marked **[harness]** in the file, in a pink **Harness** callout on the notes page, and, for stand-in components, with a **HARNESS STAND-IN** badge on screen.

Tracks: **<https://docs.copilotkit.ai/vue/agno>** and **<https://docs.copilotkit.ai/agno/generative-ui/components>**

---

## 3. Architecture

```
Browser — Vite dev server · localhost:5173
  │  @copilotkit/vue/v2; each /<route>/demo-chat mounts that page's own App.vue
  │  runtime-url="/api/copilotkit…" ──► Vite proxy /api → :8200
  ▼
Node · backend/server.ts · localhost:8200
  │  Vue Quickstart's host: createServer + createCopilotNodeListener({ cors: true })
  │  Agno landing page's runtime: my_agent = new AgnoAgent({ url: "http://localhost:8000/agui" })  (URL hard-coded)
  │  /api/copilotkit           every doc agent id → my_agent (incl. the Components samples' `default`)
  │  /api/copilotkit-threads   Intelligence quickstart's runtime (if key set)  [harness: own path]
  │  /api/copilotkit-mcp-apps  MCP Apps' runtime (mcpApps.servers)            [harness: own path]
  │  /api/copilotkit-tool-rendering  Tool Rendering's runtime: default → AgnoAgent http://localhost:8000/tool-rendering/agui  [harness: own path]
  ▼  http://localhost:8000/agui (AG-UI over HTTP)
Python · agent/harness_app.py · localhost:8000   (uv)   [harness: imports main.app unchanged]
  │  /agui  Agno Quickstart (main.py): Agent(OpenAIChat("gpt-6-luna")) → AgentOS(interfaces=[AGUI(agent)])
  │  /tool-rendering/agui  [harness, flagged] same model + description + instructions, tools=[get_weather] from src/agents/main.py (+ get_weather_impl stand-in)
  ▼
OpenAI                                    MCP Apps example server on :3101 (MCP Apps route only)
```

**Three processes.** The agent is **Python** (Agno AgentOS, FastAPI underneath). The Copilot Runtime is **TypeScript on Node** (`tsx`). The frontend is Vite.

**Where each piece comes from.**
- **The Vue Agno Quickstart redirects to a landing page.** Its `.md` is the Vue (built-in agent) Quickstart, which says to keep its Vue frontend steps and take "the runtime wiring" from your framework's quickstart. So `App.vue`, `main.ts` and the Node host come from the Vue Quickstart.
- **The landing page's only code block is the runtime**, published as a Next.js route: `agents: { my_agent: new AgnoAgent({ url: "http://localhost:8000/agui" }) }`. It's used verbatim, hosted in the Vue Quickstart's Node listener; `@ag-ui/agno` is installed in `backend/`. The URL is hard-coded, so the agent must run on :8000.
- **The agent** is the Agno Quickstart's (`/agno/quickstart`, linked as the landing page's guide): "Use an existing agent". That's `agent/main.py` verbatim, in a uv project created with the Quickstart's `uv add` line, plus one flagged dependency it needs to start (§9.2).

### Agent ids

The landing page registers only `my_agent`. The Vue samples use `default` (no agent-id), `my-agent`, `sales`, `support`, `researcher`, `workspace` and `writer`, and every one is `my_agent` (`backend/agents.ts`). Neither published page backend can run (§9.4). The Components samples keep `runtime-url="/api/copilotkit"` as published, so they run on `default` too (your choice; §9.9).

### What the adapter does (verified by capturing the model request)

- **Frontend tools:** Agno's `AGUI` interface forwards every tool in the run's `tools` to the model, so `useFrontendTool`, `useComponent`, `useHumanInTheLoop` and generative UI's `render_ui` reach the Quickstart agent with no change to `main.py`.
- **Context:** it appends the run's `context` to the user message as an `<additional context>` block. So `useAgentContext` values, and the generative UI guide (which the runtime puts in context), reach the model.
- **Not forwarded:** the run's `state`. A captured request with a state object didn't carry it, so shared-state reads don't reach the model.
- **Not provided:** backend tools, state writes and interrupts. The Quickstart agent has none, and no page publishes a usable one.

---

## 4. Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Node.js | **24.12+** (or 22.18+) | `create-vue`'s scaffold requires it. Developed on 24.16. |
| npm | 10+ | Developed on npm 12. |
| uv | 0.11+ | Runs the agent. Developed on 0.11.20. |
| Python | 3.10+ | uv picks one; developed on 3.14. |
| OpenAI API key | — | Required, in `agent/.env` (read with `uv run --env-file`). The agent uses `gpt-6-luna` as published. |
| CopilotKit Intelligence key | — | Optional, only for the two Threads routes. |

---

## 5. Setup

```bash
git clone <this-repo> agno && cd agno
cd agent && uv sync && cd ..
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
cp .env.example agent/.env              # set OPENAI_API_KEY
cp .env.example backend/.env            # optional runtime settings
```

| File | Variable | What it does |
|---|---|---|
| `agent/.env` | `OPENAI_API_KEY` | **Required.** Read by Agno's `OpenAIChat` from the environment. `main.py` loads no `.env` itself (the Quickstart `export`s the key), so the run command passes `--env-file .env`. |
| `backend/.env` | `CPK_INTELLIGENCE_API_KEY` | Optional. Intelligence for the Threads runtime: `cd backend && npx copilotkit@latest login && npx copilotkit@latest project select`. |
| `backend/.env` | `APP_USER_ID` · `MCP_APPS_URL` · `PORT` · `COPILOTKIT_TELEMETRY_DISABLED` | Optional: fixed local Threads identity (default `local-user`), MCP server URL (default `http://localhost:3101/mcp`), runtime port (default 8200), telemetry opt-out. |

**Ports:** agent **8000** (hard-coded both in the Quickstart's `main.py` and in the landing page's `AgnoAgent` URL), runtime **8200**, frontend **5173** (`strictPort`), MCP Apps example **3101**.

---

## 6. Running the project

```bash
# 1 — Agno agent: the Quickstart's app plus /tool-rendering (--env-file supplies OPENAI_API_KEY)
cd agent && uv run --env-file .env harness_app.py
```
Success: `Uvicorn running on http://0.0.0.0:8000`. (`uv run main.py`, the Quickstart's own command, also works but serves no `/tool-rendering`, so Tool Rendering fails with `HTTP 404`.) **Port 8000 must be free:** the landing page's `AgnoAgent` URL is hard-coded to `http://localhost:8000/agui`, so if something else holds 8000, the runtime talks to it.

```bash
# 2 — Copilot Runtime
cd backend && npm run dev
```
Success:
```
Copilot Runtime listening at http://localhost:8200/api/copilotkit
  Agent: AgnoAgent http://localhost:8000/agui (hard-coded on the landing page)
  + /api/copilotkit-threads  (sse)
  + /api/copilotkit-mcp-apps
  + /api/copilotkit-tool-rendering
```

```bash
# 3 — Vue app
cd frontend && npm run dev               # → http://localhost:5173/
```

Open **<http://localhost:5173>**. The landing page's **Connection** panel probes the runtime paths. **MCP Apps route only:** `cd backend && npm run mcp:apps`.

---

## 7. What to expect: walkthrough per section

Each route has a notes page (`/<route>`: notes, Try-it prompts with pass/fail, the exact source, unmounted samples as published, Harness and gap callouts) and a demo (`/<route>/demo-chat`; a **Sample** picker where a page has several samples).

### Getting Started
**`/quickstart`**: **Try:** `Hello! What can you do?` **Pass:** a streamed reply. **Fail:** connection refused or `RUN_ERROR` means the agent isn't running on :8000, or something else holds that port. A 401 means `OPENAI_API_KEY` is missing from `agent/.env`.

### Basics
**`/prebuilt-components`**, **`/custom-look-and-feel/headless-ui`**, **`/programmatic-control`**: chat against `my_agent`: a streamed reply. Headless UI streams into bare rows. Programmatic Control's default sample adds a chat (harness, on request). **`/custom-look-and-feel/slots`**: nine samples; the **Disclaimer** sample shows no disclaimer (doc bug, §9.11).
**`/prebuilt-components/copilot-threads-drawer`**, **`/headless-threads`**: need `CPK_INTELLIGENCE_API_KEY`. `/api/copilotkit-threads/info` should report `mode: "intelligence"`.
**`/frontend-tools`**: **Try:** `Only show sev1 incidents`. **Pass:** "Current filter" changes to `sev1` and the agent confirms.

### Generative UI
**`/generative-ui/tool-based`**: **Try:** `Show me the weather in Paris`. **Pass:** an inline WeatherCard.
**`/generative-ui/tool-rendering`**: runs on its own runtime path, whose `default` is the page's `get_weather` with a stand-in `get_weather_impl` (§9.4). **Try:** `What's the weather in Paris?` **Pass:** zero-config shows a `get_weather` card ending "Done"; per-tool shows the JSON result (its heading stays empty: the card reads `parameters.city`, but the tool's argument is `location`, a doc bug); catch-all shows the BrandedToolCard stand-in with the result. **Fail:** a prose answer with no tool call means the agent is `main.py`, not `harness_app.py`.
**`/generative-ui/state-rendering`**: **Expected now:** "Idle" (no backend published).
**`/generative-ui/mcp-apps`**: needs `npm run mcp:apps`. **Try:** `What time is it on the server?` **Pass:** a tool call, then an inline iframe app.

### Generative UI › Components (Vue tab of the `/agno/generative-ui/components` pages)
All run on `default`, the Quickstart agent, which receives both the `render_ui` tool and its guide (§9.9). Whether the model renders well is not yet checked against a live model.
**`/generative-ui/components`**: the overview's `App.vue` with the standard catalog. **Try:** `Compare the Starter, Team, and Enterprise plans in a table`. **Pass:** a table component in the chat.
**`/generative-ui/components/catalogs`**: your own catalog (`ProductGrid`, `ProductCard`). **Pass:** a grid of product cards.
**`/generative-ui/components/surfaces`**: a page target (`featured`) above the chat; its default content is a **stand-in** `ProductRow`. **Pass:** the agent replaces it with a ProductGrid.
**`/generative-ui/components/standard-catalog`**: standard catalog, and a sample that replaces `Card` with `MyCard`.
**`/generative-ui/components/state-and-actions`**: `ProductCard` with "Add to cart" (an `onAddToCart` event bound to an `addToCart` function). The handler sample needs `./cart-store`, which isn't published, so clicking takes the card's error path.
**`/generative-ui/components/theming`**: standard components in the amber accent and 10px radius.
**`/generative-ui/components/transports`**: tool, markdown and `agentIds: ['shop']` samples.
**`/generative-ui/components/markdown-mode`**: the guide travels in context, which Agno forwards, so the agent can answer with `a2ui` blocks. The `sendContext: false` sample puts the guide only in forwarded props, which no published Agno code reads.
**`/generative-ui/components/from-a2ui`**: the "After" provider; `Airport` and `Arrow` are **stand-ins**.

### Interactivity
**`/shared-state`**: **Try:** **Prefer concise answers**. **Pass:** `preferences.tone` appears in the agent state (Inspector › State). The notes list stays empty (§9.3).
**`/shared-state/rendering-in-app`**: the Canvas shows "Project launch", but the agent can't read or edit it (§9.3).
**`/shared-state/streaming`**: **Expected now:** "Waiting for a draft…" (no backend published).
**`/shared-state/agent-readonly`**: **Try:** `Which workspace am I in?` **Pass:** "northstar".
**`/human-in-the-loop`**: **Try:** `Schedule a meeting about Q3 planning with Dana`. **Pass:** a time-picker card (flagged stand-in); picking a slot resumes the run.
**`/human-in-the-loop/governed-actions`**: **Try:** `Refund $40 to customer 1182. Call approve_governed_action first with id a-1, tool send_refund, reference POL-7, verdict require_approval.` **Pass:** an approval card.
**`/human-in-the-loop/useInterrupt`**, **`/human-in-the-loop/headless`**: **Expected now:** no interrupt (§9.5).
**`/webmcp`**: stand-in sample only (your choice). In Chrome 149+ with WebMCP, **Run tool** `searchOrders` `{"status":"open"}` returns ORD-1001 and ORD-1004.

### Agent capabilities
**`/multi-agent/subagents`**: notes only (§9.4).

---

## 8. Testing checklist / current status

| Doc page | Route | Status | Notes |
|---|---|---|---|
| `/vue/agno` | `/` | 📖 Reference | Landing page. |
| `/vue/agno` (Quickstart) | `/quickstart` | ✅ Working | Chain verified to the model call (captured locally); needs the flagged `python-multipart` (§9.2). |
| `prebuilt-components` | same | ✅ Working | Only `CopilotChat` has code. |
| `custom-look-and-feel/slots` | same | ⚠️ Partial | Imports added to fragments; 2 stand-ins; `labels` type error; disclaimer never renders (§9.10, §9.11). |
| `custom-look-and-feel/headless-ui` | same | ✅ Working | |
| `programmatic-control` | same | ✅ Working | Default sample adds a harness chat (on request). |
| `prebuilt-components/copilot-threads-drawer` | same | ⚠️ Partial | Intelligence quickstart runtime, fixed local identity; needs a key (§9.7). |
| `headless-threads` | same | ⚠️ Partial | Same runtime (§9.7). |
| `frontend-tools` | same | ✅ Working | Adapter forwards the tool (captured). Not yet run against a live model. |
| `generative-ui/tool-based` | same | ✅ Working | Same. |
| `generative-ui/tool-rendering` | same | ⚠️ Partial | Published `get_weather` + flagged `get_weather_impl` stand-in on `/tool-rendering/agui`, own runtime path; fake-key run of the agent endpoint ran the tool; not driven live (§9.4). |
| `generative-ui/state-rendering` | same | ❌ Broken | No backend published. |
| `generative-ui/mcp-apps` | same | ⚠️ Partial | Needs `npm run mcp:apps`; placeholder URL replaced (§9.8). |
| `generative-ui/components` | same | ⚠️ Partial | `App.vue` verbatim + chart/map plugins; tool + guide reach the model; not driven live (§9.9). |
| `generative-ui/components/surfaces` | same | ⚠️ Partial | `ProductRow` stand-in; not driven live. |
| `generative-ui/components/catalogs` | same | ⚠️ Partial | Provider line wrapped with a chat; not driven live. |
| `generative-ui/components/standard-catalog` | same | ⚠️ Partial | Not driven live. |
| `generative-ui/components/state-and-actions` | same | ⚠️ Partial | `./cart-store` never published; not driven live. |
| `generative-ui/components/theming` | same | ⚠️ Partial | Not driven live. |
| `generative-ui/components/transports` | same | ⚠️ Partial | Tool and markdown: tool/guide reach the model; not driven live. |
| `generative-ui/components/markdown-mode` | same | ⚠️ Partial | Guide reaches the model via context; the `sendContext: false` sample relies on forwarded props (§9.9). |
| `generative-ui/components/from-a2ui` | same | ⚠️ Partial | `Airport`/`Arrow` stand-ins; not driven live. |
| `shared-state` | same | ⚠️ Partial | Read + tone write-back; nothing writes `notes` (§9.3). |
| `shared-state/rendering-in-app` | same | ⚠️ Partial | Canvas renders; agent can't read or write it (§9.3). |
| `shared-state/streaming` | same | ❌ Broken | No backend published. |
| `shared-state/agent-readonly` | same | ✅ Working | Agno appends context to the user message (captured). Not driven live. |
| `human-in-the-loop` | same | ⚠️ Partial | Adapter forwards the tool; `TimePickerCard` stand-in. |
| `human-in-the-loop/useInterrupt` | same | ❌ Broken | No interrupting agent published; `MeetingChat.vue` stand-in (§9.5). |
| `human-in-the-loop/headless` | same | ❌ Broken | Same; `HeadlessInterruptPanel.vue` stand-in (§9.5). |
| `human-in-the-loop/governed-actions` | same | ⚠️ Partial | Tool half forwarded; interrupt half §9.5; `executeSideEffect` undefined. |
| `webmcp` | same | ⚠️ Partial | Stand-in sample only; as published every call errors (§9.6). |
| `multi-agent/subagents` | same | ❌ Broken | Delegation tools but no supervisor; no Vue code (§9.4). |

**Legend:** ✅ Working · ⚠️ Partial · 📖 Reference · 🚧 Not started · ❌ Broken. "Working" means wired and verified from code, mounts and the captured run; **not yet driven against a live model.**

---

## 9. Known issues / doc-vs-implementation discrepancies

All against `@copilotkit/vue` / `@copilotkit/runtime` 1.87.0, `agno` 3.2.0, `@ag-ui/agno` 0.0.6, and the docs as of the 2026-11-13 baseline.

**1. The Quickstart is split across three pages.** `/vue/agno/quickstart` redirects (307) to the landing page. The root `.md` is the built-in Vue Quickstart (`BuiltInAgent`), rendered on `/vue`. The landing page renders a single code block, the runtime route, which appears in no `.md`. The agent is on the non-Vue `/agno/quickstart` "Use an existing agent" tab, which renders client-side (verified through `data-raw-code`). The landing page's runtime registers an `AgnoAgent` (`@ag-ui/agno`) with a hard-coded `http://localhost:8000/agui`, not the `HttpAgent` + `AGENT_URL` other frameworks use; `@ag-ui/agno` is installed in `backend/`.

**2. The Quickstart agent doesn't start as published (one harness fix, your choice).** `AgentOS` registers form-data routes, and the Quickstart's `uv add agno fastapi uvicorn openai ag-ui-protocol` never installs `python-multipart`, so `main.py` fails at import: `RuntimeError: Form data requires "python-multipart" to be installed`. The harness adds `python-multipart` to the uv project; `main.py` is unchanged.

**3. State never reaches the model.** A captured model request from the Quickstart agent carried the run's frontend tool and its context (appended to the user message), but not its `state`. So Shared State's tone write-back reaches the run's state but not the model, and Render state in app's Canvas can't be read or edited by the agent. [Agent Read-Only Context](https://docs.copilotkit.ai/vue/agno/shared-state/agent-readonly) does work: the page credits "the backend's CopilotKit middleware", and for Agno the AGUI interface does that job.

**4. The two page backends can't run.**
- [Tool Rendering](https://docs.copilotkit.ai/vue/agno/generative-ui/tool-rendering) prints `src/agents/main.py` (`get_weather` and other tools), which imports their implementations from `tools` and `tools.types`, modules no page publishes.
- [Sub-agents](https://docs.copilotkit.ai/vue/agno/multi-agent/subagents) prints `src/agents/subagents.py` twice; the second print contains the first. It defines the research, writing and critique sub-agents and the three delegation tools, but no page builds the supervisor agent that would use them. "Rendering a live delegation log" publishes no Vue code.

Both are kept verbatim in `agent/src/agents/` and not served as a whole. **Tool Rendering's `get_weather` is served (2026-11-17, at your request: "a route with tool agent, not a separate server").** The new `agent/harness_app.py` (flagged) imports the Quickstart's `app` and `agent` from `main.py`, unchanged. It compiles only `get_weather` from the page's file, unchanged, with the three names it uses: `json`, `tool`, and `get_weather_impl`. `get_weather_impl` comes from the unpublished `tools` module, so it is a flagged **stand-in** returning fixed sample weather (your choice). The tool runs in an Agent with the Quickstart agent's model, description and instructions, mounted on the same AgentOS app with Agno's `AGUI` interface under the `/tool-rendering` prefix (`POST /tool-rendering/agui`). The Tool Rendering samples use `default`, which every route shares, so they get their own runtime path on the same Node server, `/api/copilotkit-tool-rendering` (`backend/runtimes/tool-rendering.ts`, your choice). It uses the landing page's `AgnoAgent` with the URL `http://localhost:8000/tool-rendering/agui`, and the three `App.vue` `runtime-url`s are changed and labelled, as for MCP Apps. Verified with a fake key and a local stand-in model by posting an AG-UI run straight to the endpoint: the model was offered `get_weather`, the tool ran (`TOOL_CALL_RESULT` with the stand-in data), and the run finished. The runtime path serves its `default` agent, but a browser run through it wasn't tried, because port 8000 was in use. Per-tool's `WeatherToolCard.vue` reads `parameters.city`, but the tool's argument is `location`, so its heading stays empty (doc bug, left as published). State Rendering, State Streaming and Shared State publish no backend at all.

**5. Interrupts.** [Pausing the Agent for Input](https://docs.copilotkit.ai/vue/agno/human-in-the-loop/useInterrupt) publishes `ApprovalPanel.vue` and an `App.vue` that imports a `MeetingChat.vue` it never publishes. [Headless Interrupts](https://docs.copilotkit.ai/vue/agno/human-in-the-loop/headless) publishes only an `App.vue` that imports a never-published `HeadlessInterruptPanel.vue`. Both are flagged stand-ins (the files can't compile without them). No agent that interrupts is published, so no interrupt can fire.

**6. Undefined functions left undefined.** `searchOrders` (WebMCP: as published every call throws; the demo shows only a flagged stand-in sample, your choice), `executeSideEffect` (Governed Actions), the helpers in §9.4, and on the Components pages `useCartStore` (`./cart-store`) and `vueBasicCatalog`.

**7. Threads: Intelligence quickstart runtime.** Wired per the [Vue Agno Intelligence quickstart](https://docs.copilotkit.ai/vue/agno/intelligence/quickstart). Its `authenticateApplicationUser` is never defined; per that page's "a fixed identity is suitable only for a local, single-user demo", it returns `local-user` / "Local user" (flagged, **not authentication**). Without `CPK_INTELLIGENCE_API_KEY` the path is plain SSE, and the runtime logs that `GET /threads` returns 403. Restart the backend after `project select`. The Threads `App.vue` files use `/api/copilotkit-threads` (published value kept as a comment).

**8. MCP Apps.** The published server URL is a placeholder, replaced by the page's own `http://localhost:3101/mcp` example served by `npm run mcp:apps`. It runs on its own runtime path because `mcpApps` applies to every agent on a runtime; both `App.vue` `runtime-url`s are changed (labelled).

**9. Generative UI › Components.**
- **The pages.** The nine pages live under `/agno/generative-ui/components`, not `/vue`, and print each sample in React, Angular, React Native and Vue tabs. Only the Vue tab and untabbed code are used; tab membership is read from the snapshot's `<Tab value="Vue">` markup.
- **The agent (the ms-agent-py choice, same rules).** The overview's Vue setup includes its own runtime: a TanStack `BuiltInAgent` (`@tanstack/ai`, `openaiText("gpt-6-luna")`, `convertInputToTanStackAI`). It's shown on the route and not served. The samples keep `runtime-url="/api/copilotkit"`, so they run on the Agno Quickstart agent.
- **The guide never reaches the model.** For a run that carries a catalog, the Copilot Runtime's generative-UI middleware adds `render_ui` to the run's tools and its guide (components, props, how to call the tool) to the run's context (verified in `@copilotkit/runtime` 1.87.0's `generative-ui-middleware`). Agno's AGUI interface forwards both tools and context (§9.3), so the model gets `render_ui` with its guide, and Markdown mode's guide reaches it too. Not yet checked against a live model.
- **What the harness wrote, all flagged:**
  - Five pages print only an opening `<CopilotKitProvider …>` line (Catalogs, Transports ×3, Markdown mode's `sendContext: false`, Adopt from A2UI's "After"); the harness adds the imports, a `<CopilotChat />` and the closing tag.
  - Three pages print a provider component with a `<slot />` (Standard catalog, Theming, Markdown mode's `App.vue`); the harness puts a `<CopilotChat />` in the slot.
  - Surfaces, Standard catalog's override and State and actions get small harness pages that put the published pieces together.
  - Two modules printed without imports (State and actions' `shop-ui.ts`, Adopt from A2UI's `app-ui.ts`) get only their import lines.
  - Surfaces' `FeaturedProducts.vue` imports `../shop-ui`, which that page never prints, so the Catalogs page's `shop-ui.ts` (same `acme/shop@1`) and its two components are copied there, labelled.
  - The overview's plugin entry (`GenerativeUIChart`, `GenerativeUIMap`) is applied in the harness's `src/main.ts`, and `chart.js` and `maplibre-gl` are installed per the page.
- **Stand-ins (flagged):** `ProductRow` (Surfaces), `Airport` and `Arrow` (Adopt from A2UI).
- **Shown only:**
  - Catalogs' type-error demo and its `exportA2UICatalog` script;
  - Surfaces' recommendations sample (`Product` type never published);
  - State and actions' cart samples (`./cart-store` never published);
  - Theming's `index.html` dark-mode script, since it would affect every route;
  - Markdown mode's backend fragment (`MY_PROMPT` undefined);
  - Adopt from A2UI's "Before" (`vueBasicCatalog` undefined).

**10. Type errors** (`npm run type-check`, 9 errors), all in published doc code:
- the `labels` prop is typed as literal default strings;
- `useRenderTool`, `useDefaultRenderTool` and `useHumanInTheLoop` reject render components that declare only the props they use;
- `searchOrders` ×2;
- Surfaces' `FeaturedProducts.vue` imports `../product`, a type module no page publishes.

`npm run build` is `vite build`.

**11. Slots › Disclaimer never renders.** `CopilotChat`'s `#input` slot props don't include `showDisclaimer`, so the sample's `CopilotChatInput` never shows its `#disclaimer` slot. Left as published.

**12. Fragments, stand-ins and wrappers (Vue pages).** Slots' fragments get imports only, and "Three levels" is nested in "Two levels". Headless UI's `RenderedMessages.vue` is mounted with the minimal `HeadlessChat.vue` as its composer. Shared State's two `SharedWorkspace.vue` fragments are merged. Stand-ins: `TimePickerCard.vue`, `MeetingChat.vue`, `HeadlessInterruptPanel.vue`, `CustomMessageView`, `CustomToolbarAction`, `BrandedToolCard`, `searchOrders` (on request). `HarnessApp.vue` mounts HITL's `MeetingApproval` beside a chat. **Shown only:** `agent.subscribe`, the watch-sources line, Headless Threads' pagination, `toggleItem`, useInterrupt's multi-interrupt template, and Governed Actions' type and `handleApproval`.

**13. The harness itself.** There's no root `CopilotKitProvider`: each demo mounts its page's own `App.vue`. Doc sync runs as Vite dev-server middleware and diffs the `.md` of all 31 tracked pages, so changes to the landing runtime block or the Agno Quickstart are invisible to it. `npm run doc-files` re-reads both live. The block-catalog builder reads both backtick and tilde fences and code the rendered page carries in RSC text chunks.

---

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `RuntimeError: Form data requires "python-multipart"` | `python-multipart` missing from `agent/` | `cd agent && uv sync` (it's in `pyproject.toml`, §9.2). |
| Connection refused, or `RUN_ERROR` naming the agent URL | Agent not running on :8000 | Start terminal 1 (the URL is hard-coded to `http://localhost:8000/agui`). |
| `RUN_ERROR "HTTP 404"`, or replies from a different agent | Another server holds port 8000 | Free port 8000; the landing page's URL can't be changed without editing published code. |
| 401 / `Incorrect API key` | `OPENAI_API_KEY` missing or wrong in **`agent/.env`** | Fix it and restart the agent with `--env-file .env`. |
| Components samples answer in prose | The model chose not to render | Ask explicitly for a visual answer; check the Inspector's Generative UI tab. |
| `Agent … not found` | Backend isn't this repo's `server.ts` | Run `backend/server.ts`. |
| Threads stay on "Loading threads…" | Runtime started before the key existed (SSE → 403) | Restart the backend; the startup line must say `(intelligence)`. |
| CORS error on `/quickstart` or `/generative-ui/components` | Those `App.vue` files call `:8200` directly | Keep `cors: true`. |
| `Port 5173 is in use` | Another harness's Vite | Stop it (one harness at a time on 5173/8200). |

---

## Doc drift detection

`/doc-sync` fetches the `.md` behind all 31 tracked pages, diffs each against `doc-snapshot/pages/`, replaces the snapshot, and ranks changes High/Medium/Low. Commit `pages/`, `manifest.json` and `CHANGELOG.md`; `reports/` is gitignored. **Regenerating the doc files:** `cd frontend && npm run doc-files` does three things:
- rebuilds the block catalog (snapshot pages, plus the Agno Quickstart fetched live, every block checked against the rendered page);
- rewrites the verbatim doc files, `src/lib/published.json`, `agent/main.py` and `agent/src/agents/*.py` (`write-doc-files.py`);
- rewrites the Components routes' files (`write-genui-files.py`).

---

## 11. Project structure

```
agno/
├── CLAUDE.md · PR_GUIDELINES.md · README.md · .env.example
├── doc-snapshot/                    # pages/*.md + manifest.json — doc-sync baseline (31 pages)
├── agent/                           # Agno (Python, uv) — AgentOS :8000, AG-UI at /agui
│   ├── main.py                      # ★ Quickstart agent, verbatim
│   ├── harness_app.py               # [harness, flagged] serves main.app + /tool-rendering/agui (§9.4)
│   ├── pyproject.toml · uv.lock     # the Quickstart's `uv add` line + [harness] python-multipart
│   └── src/agents/ main.py · subagents.py   # page backends, verbatim; only main.py's get_weather is served (§9.4)
├── backend/                         # Copilot Runtime, Node :8200
│   ├── server.ts                    # ★ Vue Quickstart host + landing runtime
│   ├── agents.ts                    # AgnoAgent (landing page, verbatim) per doc agent id
│   └── runtimes/ threads.ts · mcp-apps.ts · tool-rendering.ts
└── frontend/                        # Vite + Vue 3
    ├── scripts/ build-doc-catalog.py · write-doc-files.py · write-genui-files.py · write-demo-entries.py
    └── src/ main.ts ([harness] chart/map plugins) · lib/nav-config.ts (★ routes + statuses) · routes/<doc path>/{Notes.vue, demo-chat/} · …
```

---

## 12. References

**Getting Started**: [Quickstart (landing)](https://docs.copilotkit.ai/vue/agno) · [Vue Quickstart (frontend steps)](https://docs.copilotkit.ai/vue) · [Agno Quickstart (agent)](https://docs.copilotkit.ai/agno/quickstart)

**Basics**: [Prebuilt Components](https://docs.copilotkit.ai/vue/agno/prebuilt-components) · [Slots](https://docs.copilotkit.ai/vue/agno/custom-look-and-feel/slots) · [Headless UI](https://docs.copilotkit.ai/vue/agno/custom-look-and-feel/headless-ui) · [Programmatic Control](https://docs.copilotkit.ai/vue/agno/programmatic-control) · [Threads Drawer](https://docs.copilotkit.ai/vue/agno/prebuilt-components/copilot-threads-drawer) · [Headless Threads](https://docs.copilotkit.ai/vue/agno/headless-threads) · [Frontend Tools](https://docs.copilotkit.ai/vue/agno/frontend-tools)

**Generative UI**: [Components as Tools](https://docs.copilotkit.ai/vue/agno/generative-ui/tool-based) · [Tool Call Rendering](https://docs.copilotkit.ai/vue/agno/generative-ui/tool-rendering) · [State Rendering](https://docs.copilotkit.ai/vue/agno/generative-ui/state-rendering) · [MCP Apps](https://docs.copilotkit.ai/vue/agno/generative-ui/mcp-apps)

**Generative UI › Components**: [Components and surfaces](https://docs.copilotkit.ai/agno/generative-ui/components) · [Surfaces](https://docs.copilotkit.ai/agno/generative-ui/components/surfaces) · [Catalogs](https://docs.copilotkit.ai/agno/generative-ui/components/catalogs) · [Standard catalog](https://docs.copilotkit.ai/agno/generative-ui/components/standard-catalog) · [State and actions](https://docs.copilotkit.ai/agno/generative-ui/components/state-and-actions) · [Theming](https://docs.copilotkit.ai/agno/generative-ui/components/theming) · [Transports](https://docs.copilotkit.ai/agno/generative-ui/components/transports) · [Markdown mode](https://docs.copilotkit.ai/agno/generative-ui/components/markdown-mode) · [Adopt from A2UI](https://docs.copilotkit.ai/agno/generative-ui/components/from-a2ui)

**Interactivity**: [Shared State](https://docs.copilotkit.ai/vue/agno/shared-state) · [Render agent state in your app](https://docs.copilotkit.ai/vue/agno/shared-state/rendering-in-app) · [State Streaming](https://docs.copilotkit.ai/vue/agno/shared-state/streaming) · [Agent Read-Only Context](https://docs.copilotkit.ai/vue/agno/shared-state/agent-readonly) · [HITL Overview](https://docs.copilotkit.ai/vue/agno/human-in-the-loop) · [Pausing the Agent for Input](https://docs.copilotkit.ai/vue/agno/human-in-the-loop/useInterrupt) · [Headless Interrupts](https://docs.copilotkit.ai/vue/agno/human-in-the-loop/headless) · [Governed Action Approval UI](https://docs.copilotkit.ai/vue/agno/human-in-the-loop/governed-actions) · [WebMCP](https://docs.copilotkit.ai/vue/agno/webmcp)

**Agent capabilities**: [Sub-agents](https://docs.copilotkit.ai/vue/agno/multi-agent/subagents)

**Intelligence (Threads routes)**: [Connect Intelligence in 5 minutes](https://docs.copilotkit.ai/vue/agno/intelligence/quickstart)
