<script lang="ts">
	import { modalStore } from '$lib/stores/modal_markdown';

	import { onDestroy } from 'svelte';
	import Markdown from 'svelte-exmarkdown';

	let showModal = false;
	let content = '';
	let title = '';

	const unsubscribe = modalStore.subscribe(
		({ showModal: visible, content: modalContent, title: modalTitle }) => {
			showModal = visible;
			content = modalContent;
			title = modalTitle;
		}
	);

	onDestroy(() => {
		unsubscribe();
	});

	function closeModal() {
		modalStore.set({ showModal: false, content: '', title: '' });
	}
</script>

{#if showModal}
	<dialog open class="modal">
		<div class="modal-box w-11/12 max-w-5xl">
			<h3 class="font-bold text-lg">{title}</h3>
			<div class="divy-4"><Markdown md={content}></Markdown></div>
			<div class="modal-action">
				<button class="btn" on:click={closeModal}>Close</button>
			</div>
		</div>
	</dialog>
{/if}
