<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { lock } from '$lib/api';

	let { children } = $props();

	async function handleLock() {
		if ($auth.isAuthenticated) {
			await lock($auth.username, $auth.password);
			auth.logout();
			goto('/');
		}
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Logbook</title>
</svelte:head>

<nav>
	<a href="/">Logbook</a>
	{#if $auth.isAuthenticated}
		<a href="/chronicle">Chronicle</a>
		<a href="/entries/new">New Entry</a>
		<a href="/profile">Profile</a>
		<button onclick={handleLock}>Lock</button>
	{:else}
		<a href="/unlock">Unlock</a>
		<a href="/enlist">Enlist</a>
	{/if}
</nav>

<main>
	{@render children()}
</main>

<style>
	:global(body) {
		font-family: system-ui, -apple-system, sans-serif;
		margin: 0;
		padding: 0;
		background: #f5f5f5;
	}

	nav {
		background: #333;
		padding: 1rem;
		display: flex;
		gap: 1rem;
		align-items: center;
	}

	nav a {
		color: white;
		text-decoration: none;
	}

	nav a:hover {
		text-decoration: underline;
	}

	nav button {
		background: none;
		border: 1px solid white;
		color: white;
		padding: 0.25rem 0.5rem;
		cursor: pointer;
	}

	nav button:hover {
		background: white;
		color: #333;
	}

	main {
		max-width: 800px;
		margin: 2rem auto;
		padding: 0 1rem;
	}

	:global(h1, h2, h3) {
		margin-top: 0;
	}

	:global(form) {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		max-width: 400px;
	}

	:global(label) {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	:global(input, textarea, select) {
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 1rem;
	}

	:global(textarea) {
		min-height: 100px;
		resize: vertical;
	}

	:global(button[type='submit']) {
		background: #333;
		color: white;
		border: none;
		padding: 0.75rem 1rem;
		cursor: pointer;
		border-radius: 4px;
	}

	:global(button[type='submit']:hover) {
		background: #555;
	}

	:global(.error) {
		color: #c00;
		background: #fee;
		padding: 0.5rem;
		border-radius: 4px;
	}

	:global(.success) {
		color: #060;
		background: #efe;
		padding: 0.5rem;
		border-radius: 4px;
	}

	:global(.entry) {
		background: white;
		padding: 1rem;
		margin-bottom: 1rem;
		border-radius: 4px;
		border: 1px solid #ddd;
	}

	:global(.entry-meta) {
		font-size: 0.875rem;
		color: #666;
		margin-top: 0.5rem;
	}

	:global(.entry-actions) {
		margin-top: 0.5rem;
		display: flex;
		gap: 0.5rem;
	}

	:global(.entry-actions a, .entry-actions button) {
		font-size: 0.875rem;
		padding: 0.25rem 0.5rem;
		background: #eee;
		border: 1px solid #ccc;
		border-radius: 4px;
		text-decoration: none;
		color: #333;
		cursor: pointer;
	}

	:global(.entry-actions a:hover, .entry-actions button:hover) {
		background: #ddd;
	}

	:global(.danger) {
		background: #c00 !important;
		color: white !important;
		border-color: #900 !important;
	}

	:global(.danger:hover) {
		background: #900 !important;
	}
</style>
