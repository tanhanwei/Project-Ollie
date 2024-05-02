<script lang="ts">
	import type { LayoutData } from './$types';
	import '../app.css';
	import { allChats, currentChat, isChatSelected } from '$lib/stores/current_chat';
	import type { ChatModel } from '$lib/models/chat_model';
	import { onMount } from 'svelte';
	import { io } from 'socket.io-client';
	import Markdown from 'svelte-exmarkdown';

	let text = '';
	let allAgents: string[] = [];

	let activeAgents: string[] = [];
	let chatContainer: HTMLElement;
	let loading = false;

	let messages: any[] = [];

	const scrollToBottom = async (node: any) => {
		node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
	};

	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault(); // Prevent the default behavior of Enter key
			onSend(text, true); // Assuming onSend is a function to handle sending the text
			scrollToBottom(chatContainer);
		}
	}

	onMount(() => {
		getAllAgents();

		const baseUrl = window.location.origin; // Dynamically get the base URL
		const socket = io(baseUrl); // Connect to WebSocket server at the same base URL

		socket.on('connect', () => {
			console.log('Connected to the server!');
		});

		socket.on('debug', (data) => {
			console.log('Debug:', data.message); // Ensure this matches the event name and logs correctly

			messages = [...messages, data.message]; // Update messages array with new message
		});

		socket.on('disconnect', () => {
			console.log('Disconnected from server');
			socket.close();
		});

		return () => {
			socket.close();
		};
	});

	async function onNewChat() {
		await createManager();
		isChatSelected.set(false);
		currentChat.set(null);
	}

	async function getAllAgents() {
		let url = './get-agents';

		await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then((response) => response.json())
			.then((data) => {
				console.log('Success:', data);
				allAgents = data['agents'];
			})
			.catch((error) => {
				console.error('Error:', error);
			});
	}

	async function createManager() {
		let url = './create-manager';

		let response = await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then((response) => response.json())
			.then((data) => {
				console.log('Success:', data);
			})
			.catch((error) => {
				console.error('Error:', error);
			});
	}

	async function callAPI() {
		if (text === '') {
			return;
		}

		loading = true;

		let url = './api';

		await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				input: text,
				agent_keys: activeAgents
			})
		})
			.then((response) => response.json())
			.then((data) => {
				console.log('Success:', data);

				let responseData = data['response'];
				onSend(responseData, false, false);
			})
			.catch((error) => {
				console.error('Error:', error);
			});

		loading = false;
	}

	async function onSend(newMessage: string, isUserInput: boolean, useAPI: boolean = true) {
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

			if (useAPI == true) {
				await callAPI();
			}

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

		if (useAPI == true) {
			await createManager();
			await callAPI();
		}

		text = '';
	}

	function onChatSelect(chatModel: ChatModel) {
		isChatSelected.set(true);
		currentChat.set(chatModel);
	}

	function toggleAgent(agent: string) {
		let index = activeAgents.indexOf(agent);

		if (index > -1) {
			activeAgents = activeAgents.filter((item) => item !== agent);
		} else {
			activeAgents = [...activeAgents, agent];
		}
	}
</script>

<div class="flex flex-row">
	<div class="drawer lg:drawer-open">
		<input id="my-drawer-2" type="checkbox" class="drawer-toggle" />

		<div class="drawer-content flex flex-col justify-between items-center">
			<!-- svelte-ignore a11y-label-has-associated-control -->
			<label class="navbar shadow-xl bg-base-200 flex flex-row justify-between px-3">
				<label for="my-drawer-2" class="btn btn-ghost drawer-button lg:hidden">Menu</label>

				<div class=" font-bold text-[18px]">Mini Gemini</div>
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
							"Which new movie is getting the most attention on reddit?"
						</div>
					</div>
				</div>
			{/if}

			<div>
				{#if $isChatSelected === true}
					<div
						bind:this={chatContainer}
						class=" flex flex-col-reverse h-[calc(100vh-200px)] overflow-y-scroll"
					>
						<slot></slot>
					</div>
				{/if}

				<div class="flex flex-row w-full rounded-t-md items-center justify-center px-3">
					<div class="flex flex-row justify-start items-center">
						<div class="bg-base-100 rounded-2xl w-[600px] mb-3">
							<div class="px-5 py-1 text-left"></div>
						</div>
					</div>
				</div>
				<div class="flex flex-row w-full rounded-t-md items-center justify-center">
					{#if loading == false}
						<form
							class="m-3 flex flex-row w-full rounded-t-md"
							on:submit|preventDefault={() => {
								console.log('submit');
							}}
						>
							<textarea
								placeholder="Ask away!"
								class=" textarea textarea-md textarea-primary textarea-bordered rounded-2xl text-secondary-content max-h-32 mr-3 w-full"
								bind:value={text}
								on:keydown={handleKeyDown}
							/>
							<button
								class="btn btn-primary btn-lg rounded-2xl"
								type="submit"
								on:click={async () => {
									await onSend(text, true);
									scrollToBottom(chatContainer);
								}}>Send</button
							>
						</form>
					{:else}
						<div class="loading loading-dots loading-lg text-primary mb-5" />
					{/if}
				</div>
			</div>

			<!-- text box at end of the page -->
		</div>
		<div class="drawer-side">
			<label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label>
			<ul class="menu bg-base-300 p-0 w-72 min-h-full text-base-content flex flex-col">
				<!-- svelte-ignore a11y-label-has-associated-control -->
				<label class="navbar bg-base-200 shadow-xl shadow-gray-50 justify-between">
					<div class="text-secondary-content font-bold ml-3 text-[18px]">Your Chats</div>
					<div class="flex flex-row">
						<!-- svelte-ignore a11y-click-events-have-key-events -->
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<div
							class="btn btn-primary btn-sm rounded-xl mr-3"
							on:click={async () => {
								await onNewChat();
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

				<div class="mx-5 flex flex-col h-44 overflow-y-aut">
					{#each allAgents as agent}
						<!-- toggle -->
						<div class="form-control mb-3 bg-secondary p-2 rounded-xl">
							<label class="label cursor-pointer">
								<span class="label-text text-secondary-content">{agent}</span>
								<input
									type="checkbox"
									class="toggle toggle-primary toggle-sm"
									on:change={() => {
										toggleAgent(agent);
									}}
								/>
							</label>
						</div>
					{/each}
				</div>
			</ul>
		</div>
	</div>

	<div class="w-[350px] h-screen bg-base-200 overflow-y-auto">
		<div class="flex flex-row justify-between items-center h-16 relative">
			<div class="text-secondary-content font-bold mx-4 mt-4 mb-3 text-[18px]">Server Logs</div>
			<!-- svelte-ignore a11y-no-static-element-interactions -->
			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<div
				class="btn btn-primary btn-sm rounded-xl mx-4 mt-4 mb-3"
				on:click={() => {
					messages = [];
				}}
			>
				Clear Logs
			</div>
		</div>

		<div class="divider opacity-40 rounded-md mx-4 my-0 bg-base-200"></div>
		<div class="p-5 flex flex-col h-[calc(100vh-100px)] overflow-y-scroll">
			{#each messages as message}
				<div class="bg-secondary opacity-50 rounded-2xl mb-3">
					<div class="text-secondary-content p-5"><Markdown md={message}></Markdown></div>
				</div>
			{/each}
		</div>
	</div>
</div>
