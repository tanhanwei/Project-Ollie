<script lang="ts">
	import ChatBubble from '$lib/components/ChatBubble.svelte';
	import { currentChat, isChatSelected } from '$lib/stores/current_chat';
	import type { LayoutData } from './$types';

	let activeAgents = ['Steam', 'Reddit'];
</script>

<div>
	<div class="flex flex-row w-full rounded-t-md items-center justify-center px-3">
		<div class="flex flex-row justify-start items-center">
			<div class="bg-base-100 rounded-2xl w-[600px] mb-3">
				<div class="px-5 py-1 text-left"></div>
			</div>
		</div>
	</div>
	{#if $isChatSelected && $currentChat != null}
		{#each $currentChat.messages as message}
			<ChatBubble chatData={message} />
		{/each}
	{/if}
</div>
