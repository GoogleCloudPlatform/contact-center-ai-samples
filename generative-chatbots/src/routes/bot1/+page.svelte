<script lang="ts">
  import { onMount } from "svelte";

  onMount(() => {
    const script = document.createElement("script");
    script.src = "https://www.gstatic.com/dialogflow-console/fast/messenger-cx/bootstrap.js?v=1";
    script.async = true;
    document.head.appendChild(script);
  });
</script>

<div>
  <df-messenger
    df-cx="true"
    chat-title="Generative AI Agent"
    agent-id="5e361182-376a-4507-bfa2-a394cb7e9c8e"
    language-code="en"
    expand="true" />
</div>
