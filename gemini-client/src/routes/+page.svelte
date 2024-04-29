<script lang="ts">
	import ChatBubble from '$lib/components/ChatBubble.svelte';
	import { currentChat, isChatSelected } from '$lib/stores/current_chat';
	import type { LayoutData } from './$types';

	let activeAgents = ['Steam', 'Reddit'];
</script>

{#if $isChatSelected && $currentChat != null}
	<div>
		{#each $currentChat.messages as message}
			<ChatBubble chatData={message} />
		{/each}
	</div>
{/if}
