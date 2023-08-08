<script lang="ts">
	import { onMount } from 'svelte';

	onMount(() => {
		const script = document.createElement('script');
		script.src = 'https://www.gstatic.com/dialogflow-console/fast/messenger-cx/bootstrap.js?v=1';
		script.async = true;
		document.head.appendChild(script);
	});
</script>

<div>
	<df-messenger
		df-cx="true"
		chat-title="Vertex AI - PaLM API"
		agent-id="a961ff0c-1bc9-4fa7-afb6-b8c640811358"
		language-code="en"
		expand="true"
	/>
</div>
