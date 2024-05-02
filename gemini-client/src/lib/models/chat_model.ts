export interface ChatModel {
	id: string;
	messages: MessageModel[];
}

export interface MessageModel {
	isUserInput: boolean;
	message: string;
	agent: string;
	markdown: MarkdownModel[];
}

export interface MarkdownModel {
	agent: string;
	md: string;
}
