<script lang="ts">
	import type { MessageModel } from '$lib/models/chat_model';
	import { writable } from 'svelte/store';

	export let chatData: MessageModel;
</script>

<!-- create a message bubble based on data, the left side will be if not user input and right side if user input -->

<div class="flex flex-row justify-center items-center">
	{#if chatData.isUserInput === false}
		<div class="flex flex-row justify-start items-center">
			<div class="bg-secondary rounded-2xl w-[600px] mb-3">
				<div class="text-secondary-content px-5 py-3 text-left">
					{chatData.message}
				</div>
			</div>
		</div>
	{:else}
		<div class="flex flex-row justify-end items-center">
			<div class="bg-primary rounded-2xl w-[600px] mb-3">
				<div class="text-primary-content px-5 py-3 text-right">
					{chatData.message}
				</div>
			</div>
		</div>
	{/if}
</div>
