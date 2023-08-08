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
    chat-title="Generative AI Agent + Generative Fallback"
    agent-id="84940117-61b9-4f2e-ba77-730a28de2e31"
    language-code="en"
    expand="true" />
</div>
