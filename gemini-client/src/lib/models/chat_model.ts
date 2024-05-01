export interface ChatModel {
	id: string;
	messages: MessageModel[];
}

export interface MessageModel {
	isUserInput: boolean;
	message: string;
	agent: string;
}
