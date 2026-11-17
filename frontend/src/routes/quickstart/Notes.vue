<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
</script>

<template>
  <RouteHeader path="/quickstart" />

  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
      The whole stack, assembled from the three places the docs put it: the Vue app from the Vue Quickstart (<code>App.vue</code> with
      <code>CopilotChat</code>), the runtime from the Agno landing page (an <code>AgnoAgent</code> from <code>@ag-ui/agno</code> named <code>my_agent</code>,
      pointed at <code>http://localhost:8000/agui</code>) hosted in the Vue Quickstart's Node <code>server.ts</code>, and the agent from the Agno
      Quickstart (<code>main.py</code>: an <code>Agent</code> on <code>OpenAIChat</code>, in an <code>AgentOS</code> with the <code>AGUI</code> interface at <code>/agui</code>). Three
      processes: the agent on :8000, the runtime on :8200, Vite on :5173.
    </p>
    <div class="mt-4">
      <TryIt
        :prompts="['Hello! What can you do?', 'Write a haiku about rivers.']"
        expect="A streamed reply from the Agno agent; the Inspector's AG-UI Events show RUN_STARTED → TEXT_MESSAGE_* → RUN_FINISHED."
        fail="Connection refused or RUN_ERROR — the agent is not running on :8000 or AGENT_URL is unset; a 401 — OPENAI_API_KEY missing in agent/.env (or the Azure OpenAI variables)."
      />
    </div>
  </Panel>

  <Panel title="The demo" description="Verbatim src/App.vue from the Vue Quickstart, which the Agno Vue Quickstart's .md is.">
    <SourceCode file="frontend/src/routes/quickstart/demo-chat/App.vue" />
  </Panel>

  <Panel title="The runtime, as published on the Agno landing page" description="Its only code block — a Next.js route.">
    <PublishedCode page="index" :index="9" />
  </Panel>

  <Panel title="This repo's runtime" description="The Vue Quickstart's Node host with the landing page's agent registration; additions marked [harness].">
    <div class="space-y-4">
      <SourceCode file="backend/server.ts" />
      <SourceCode file="backend/agents.ts" />
    </div>
  </Panel>

  <Panel title="The agent — Agno Quickstart, “Use an existing agent”" description="main.py verbatim. Run with uv run main.py, as the Quickstart says.">
    <SourceCode file="agent/main.py" />
  </Panel>

  <Callout tone="harness" title="One harness change so the Quickstart agent starts (your choice, README §9.2)">
    <p>· <strong><code>python-multipart</code> added</strong> to the agent's uv project: <code>AgentOS</code> registers form-data routes, and the Quickstart's <code>uv add agno fastapi uvicorn openai ag-ui-protocol</code> line never installs it (<code>RuntimeError: Form data requires "python-multipart" to be installed</code>). <code>main.py</code> is unchanged.</p>
  </Callout>

  <Panel title="The Vue Quickstart's server.ts and main.ts, as published">
    <div class="space-y-4">
      <PublishedCode page="index" :index="4" note="Host only — its BuiltInAgent registration is replaced by the landing page's AgnoAgent, as the Vue Quickstart itself instructs for an existing agent." />
      <PublishedCode page="index" :index="5" />
    </div>
  </Panel>

  <Callout tone="harness" title="How the three sources fit (README §3, §9.1)">
    <p>· <strong>The Vue Agno Quickstart redirects to a landing page.</strong> Its .md is the built-in Vue Quickstart, which says: if you already have an agent, keep its Vue frontend steps and take the runtime wiring from your framework's quickstart.</p>
    <p>· <strong>The landing page</strong> publishes only the runtime route (<code>my_agent: new AgnoAgent({ url: "http://localhost:8000/agui" })</code>, the URL hard-coded), as a Next.js route; a Vue app has no Next route, so it is hosted in the Vue Quickstart's Node listener.</p>
    <p>· <strong>The agent</strong> is from the Agno Quickstart the landing page links as its guide: the “Use an existing agent” path — an <code>Agent</code> on <code>OpenAIChat(id="gpt-6-luna", reasoning_effort="none")</code>, wrapped in <code>AgentOS(agents=[agent], interfaces=[AGUI(agent=agent)])</code> and served with <code>agent_os.serve(app="main:app", port=8000)</code>.</p>
    <p>· The runtime also registers the doc agent ids (<code>backend/agents.ts</code>); each is <code>my_agent</code>.</p>
  </Callout>

  <Callout tone="info" title="What this agent can and cannot do (README §3)">
    <p>Agno's <code>AGUI</code> interface forwards every CopilotKit frontend tool to the model and appends the run's context to the user message (an <code>&lt;additional context&gt;</code> block), so frontend tools, HITL and read-only context work with no change to <code>main.py</code> (verified by capturing the model request). The run's state does not reach the model, so shared-state reads and writes are gaps. It has no backend tools and never interrupts.</p>
  </Callout>
</template>
