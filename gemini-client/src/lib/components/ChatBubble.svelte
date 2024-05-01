<script lang="ts">
	import type { MessageModel } from '$lib/models/chat_model';
	import { writable } from 'svelte/store';
	import Markdown from 'svelte-exmarkdown';

	export let chatData: MessageModel;
</script>

<!-- create a message bubble based on data, the left side will be if not user input and right side if user input -->

<div class="flex flex-row w-full rounded-t-md items-center justify-center px-3">
	{#if chatData.isUserInput === false}
		<div class="flex flex-row justify-start items-center">
			<div class="bg-secondary rounded-2xl w-[600px] mb-3">
				<div class="px-5 py-3 text-left">
					<Markdown md={chatData.message}></Markdown>
				</div>
			</div>
		</div>
	{:else}
		<div class="flex flex-row justify-end items-center">
			<div class="bg-base-300 rounded-2xl w-[600px] mb-3">
				<div class=" px-5 py-3 text-right">
					<Markdown md={chatData.message}></Markdown>
				</div>
			</div>
		</div>
	{/if}
</div>
