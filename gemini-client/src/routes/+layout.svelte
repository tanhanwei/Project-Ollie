<script lang="ts">
	import type { LayoutData } from './$types';
	import '../app.css';
	import { allChats, currentChat, isChatSelected } from '$lib/stores/current_chat';
	import type { ChatModel } from '$lib/models/chat_model';

	let text = '';
	let activeAgents = ['Steam', 'Reddit'];

	function onNewChat() {
		isChatSelected.set(false);
		currentChat.set(null);
	}

	function checkIfChatIsSelectedFromAll() {}

	function onSend(newMessage: string, isUserInput: boolean) {
		if (newMessage === '') {
			return;
		}

		if ($isChatSelected == true) {
			let currentMessages = $currentChat?.messages ?? [];

			// add message to current chat and update the store with new chat & update all chats
			currentMessages.push({
				agent: '',
				message: newMessage,
				isUserInput: isUserInput
			});

			$currentChat!.messages = currentMessages;

			allChats.update((chats) => {
				if (!$currentChat || $currentChat == null) {
					return chats;
				}

				const index = chats.findIndex((chat) => chat.id === $currentChat!.id);
				chats[index] = $currentChat;
				return chats;
			});

			text = '';
			return;
		}

		// create new chat and add message to it

		let uuid = Math.random().toString(36).substring(7);

		let newChat: ChatModel = {
			id: uuid,
			messages: [
				{
					agent: '',
					message: newMessage,
					isUserInput: true
				}
			]
		};

		allChats.update((chats) => {
			chats.push(newChat);
			return chats;
		});

		currentChat.set(newChat);
		isChatSelected.set(true);
		text = '';
	}

	function onChatSelect(chatModel: ChatModel) {
		currentChat.set(chatModel);
	}
</script>

<div class="drawer lg:drawer-open">
	<input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
	<div class="drawer-content flex flex-col justify-between items-center">
		<label class="navbar shadow-xl shadow-gray-50 flex flex-row justify-between px-3">
			<label for="my-drawer-2" class="btn btn-ghost drawer-button lg:hidden">Menu</label>

			<div class=" font-bold text-[18px]">Google 2024 Gemini Hackathon!</div>
		</label>

		{#if $isChatSelected !== true}
			<div class="grid grid-cols-2">
				<div class="bg-secondary opacity-50 rounded-2xl w-[350px] mr-5">
					<div class="text-secondary-content p-5 text-center">
						Start asking quesitons, I am ready to answer!
					</div>
				</div>

				<div class="bg-secondary opacity-50 rounded-2xl w-[350px]">
					<div class="text-secondary-content p-5 text-center">
						"What are the latest sentiments about Cyeberpunk 2077?"
					</div>
				</div>

				<div class="bg-secondary opacity-50 rounded-2xl w-[350px] mt-5 mr-5">
					<div class="text-secondary-content p-5 text-center">
						"Which games are trending in the market?"
					</div>
				</div>

				<div class="bg-secondary opacity-50 rounded-2xl w-[350px] mt-5">
					<div class="text-secondary-content p-5 text-center">
						"Which new moive is getting the most attention on reddit?"
					</div>
				</div>
			</div>
		{/if}

		<div>
			<slot></slot>

			<div class="flex flex-row w-full rounded-t-md items-center justify-center">
				<input
					type="text"
					placeholder="Ask away!"
					class=" input input-lg input-primary input-bordered m-3 rounded-2xl w-[382px] text-secondary-content"
					bind:value={text}
				/>
				<button
					class="btn btn-primary btn-lg rounded-2xl"
					on:click={() => {
						onSend(text, true);
					}}>Send</button
				>
				<button
					class="ml-2 btn btn-primary btn-lg rounded-2xl"
					on:click={() => {
						onSend(text, false);
					}}>Agent</button
				>
			</div>
		</div>

		<!-- text box at end of the page -->
	</div>
	<div class="drawer-side">
		<label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label>
		<ul class="menu bg-base-300 p-0 w-72 min-h-full text-base-content flex flex-col">
			<label class="navbar bg-base-200 shadow-xl shadow-gray-50 justify-between">
				<div class="text-secondary-content font-bold ml-3 text-[18px]">Your Chats</div>
				<div class="flex flex-row">
					<div
						class="btn btn-primary btn-sm rounded-xl mr-3"
						on:click={() => {
							onNewChat();
						}}
					>
						New Chat
					</div>
				</div>
			</label>

			{#if $allChats.length == 0}
				<div class="bg-secondary opacity-50 rounded-2xl mx-5 my-3">
					<div class="text-secondary-content p-5 m-0 text-center">Start a new chat with me!</div>
				</div>
			{/if}

			<div class="mx-5 mt-2">
				<!-- all chat id as button -->
				{#each $allChats as chat}
					{#if chat.id == $currentChat?.id}
						<button
							class="btn btn-primary rounded-xl text-left mb-3 w-full"
							on:click={() => {
								onChatSelect(chat);
							}}>{chat.id}</button
						>
					{:else}
						<button
							class="btn btn-secondary rounded-xl text-left mb-3 w-full"
							on:click={() => {
								onChatSelect(chat);
							}}>{chat.id}</button
						>
					{/if}
				{/each}
			</div>

			<div class="divider opacity-40 rounded-md m-0 mx-5"></div>
			<div class="text-secondary-content font-bold ml-5 mt-5 mb-5 text-[18px]">Active Agents</div>

			<div class="mx-5">
				{#each activeAgents as agent}
					<!-- toggle -->
					<div class="form-control mb-3 bg-secondary p-2 rounded-xl">
						<label class="label cursor-pointer">
							<span class="label-text text-secondary-content">{agent}</span>
							<input type="checkbox" class="toggle toggle-primary toggle-sm" checked />
						</label>
					</div>
				{/each}
			</div>
		</ul>
	</div>
</div>
