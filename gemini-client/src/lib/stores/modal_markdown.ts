// modalStore.js
import { writable } from 'svelte/store';

export const modalStore = writable({
	showModal: false,
	content: '',
	title: ''
});
