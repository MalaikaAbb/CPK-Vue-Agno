<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
const D = "frontend/src/routes/generative-ui/tool-rendering/demo-chat";
</script>

<template>
  <RouteHeader path="/generative-ui/tool-rendering" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
      Three ways to draw a tool call — the built-in <code>*</code> renderer, a custom catch-all, and a per-tool <code>useRenderTool</code> for
      <code>get_weather</code> — for the page's backend tool, <code>get_weather</code>.
    </p>
    <div class="mt-4">
      <TryIt :prompts="['What is the weather in Tokyo?']" expect="Zero-config: a get_weather status card that ends “Done”. Per-tool: the JSON result under an empty heading (the card reads parameters.city, but the tool's argument is location — doc bug). Catch-all: the BrandedToolCard stand-in with the result." fail="A prose answer and no tool call: the agent server is running main.py instead of harness_app.py (no /tool-rendering), or the model skipped the tool." />
    </div>
  </Panel>
  <Panel title="Published files, mounted verbatim">
    <div class="space-y-4">
      <SourceCode :file="`${D}/default/components/AgentExperience.vue`" />
      <SourceCode :file="`${D}/per-tool/components/WeatherToolCard.vue`" />
      <SourceCode :file="`${D}/per-tool/components/AgentExperience.vue`" />
      <SourceCode :file="`${D}/per-tool/App.vue`" note="The same published App.vue is copied into each variant directory, unchanged." />
    </div>
  </Panel>
  <Panel title="The page's backend, verbatim (only get_weather is served)"><SourceCode file="agent/src/agents/main.py" note="Tool Rendering's src/agents/main.py: get_weather and more, imported from a `tools` module (and tools.types) no page publishes. Only get_weather is served (see below)." /></Panel>
  <Callout tone="info" title="Agent: the page's get_weather on /tool-rendering (README §9.4)">
    <p>The page's backend file can't be imported, because it pulls helpers from a <code>tools</code> module that no page publishes. So <code>agent/harness_app.py</code> compiles only its <code>get_weather</code> function, unchanged, from <code>agent/src/agents/main.py</code>. It gives that function a flagged <code>get_weather_impl</code> stand-in that returns fixed sample weather, and serves it as a tool agent at <code>/tool-rendering/agui</code> on the same agent server. The three samples reach it through their own runtime path, <code>/api/copilotkit-tool-rendering</code> (its <code>default</code> is that agent), so every other route keeps the Quickstart agent. Checked on 2026-11-17 with a fake key and a local stand-in model: the tool ran and all three renderers drew the call. Not yet driven against a live model.</p>
  </Callout>
  <Panel title="Custom catch-all" description="The page prints only one line for this file.">
    <div class="space-y-4">
      <PublishedCode page="generative-ui__tool-rendering" :index="1" />
      <SourceCode :file="`${D}/catch-all/components/AgentExperience.vue`" />
      <SourceCode :file="`${D}/catch-all/components/BrandedToolCard.vue`" />
    </div>
  </Panel>
  <Panel title="Published, not mounted">
    <PublishedCode page="generative-ui__tool-rendering" :index="4" note="Fragment: `parameters` and `locale` are never declared." />
  </Panel>
  <Callout tone="harness" title="What the harness added">
    <p>· The catch-all <code>AgentExperience.vue</code> wraps the published line; <code>BrandedToolCard</code> is a stand-in — never published.</p>
    <p>· The three <code>App.vue</code> files use <code>runtime-url="/api/copilotkit-tool-rendering"</code> (the published value is kept as a comment); <code>backend/runtimes/tool-rendering.ts</code> serves it from the same Node server.</p>
    <p>· <code>agent/harness_app.py</code>: the published <code>get_weather</code> plus a <code>get_weather_impl</code> <strong>stand-in</strong> (fixed sample data, never published), on the Quickstart's model and prompt.</p>
  </Callout>
</template>
