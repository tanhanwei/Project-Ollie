import type { ChatModel } from '$lib/models/chat_model';
import { writable, type Writable } from 'svelte/store';

export const isChatSelected: Writable<boolean> = writable(false);

export const allChats: Writable<ChatModel[]> = writable([]);

export const currentChat: Writable<ChatModel | null> = writable(null);

export const chatInput: Writable<string> = writable('');

// all chats functions
export class ChatStore {
	static addChat(chat: ChatModel) {
		allChats.update((chats) => {
			return [...chats, chat];
		});
	}

	static removeChat(id: string) {
		allChats.update((chats) => {
			return chats.filter((chat) => chat.id !== id);
		});
	}

	static updateChat(chat: ChatModel) {
		allChats.update((chats) => {
			return chats.map((c) => {
				if (c.id === chat.id) {
					return chat;
				}
				return c;
			});
		});
	}
}
