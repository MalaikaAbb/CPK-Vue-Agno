<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
</script>

<template>
  <RouteHeader path="/multi-agent/subagents" />
  <Callout tone="warn" title="Gap: delegation tools, no supervisor, no frontend (README §9.4)">
    <p>· <code>src/agents/subagents.py</code> (printed twice; the second print contains every line of the first) defines the research, writing and critique sub-agents and the <code>research_agent</code> / <code>writing_agent</code> / <code>critique_agent</code> delegation tools, which record delegations through <code>run_context</code>. No page builds the supervisor agent that would use them, or serves it. Per your rules nothing was written in its place; it is not served.</p>
    <p>· The “Rendering a live delegation log” section publishes no Vue code, so this route has no demo.</p>
  </Callout>
  <Panel title="Published backend, verbatim, not served"><SourceCode file="agent/src/agents/subagents.py" /></Panel>
</template>
