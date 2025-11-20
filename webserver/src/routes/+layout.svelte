<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { lock } from '$lib/api';
	import { onMount } from 'svelte';

	// Import Bootstrap CSS (safe for SSR)
	import 'bootstrap/dist/css/bootstrap.min.css';

	// Import Bootstrap JS only on client side (requires document)
	onMount(async () => {
		await import('bootstrap/dist/js/bootstrap.bundle.min.js');
	});

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

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
	<div class="container">
		<a class="navbar-brand" href="/">Logbook</a>
		<button
			class="navbar-toggler"
			type="button"
			data-bs-toggle="collapse"
			data-bs-target="#navbarNav"
			aria-controls="navbarNav"
			aria-expanded="false"
			aria-label="Toggle navigation"
		>
			<span class="navbar-toggler-icon"></span>
		</button>
		<div class="collapse navbar-collapse" id="navbarNav">
			<ul class="navbar-nav ms-auto">
				{#if $auth.isAuthenticated}
					<li class="nav-item">
						<a class="nav-link" href="/chronicle">Chronicle</a>
					</li>
					<li class="nav-item">
						<a class="nav-link" href="/entries/new">New Entry</a>
					</li>
					<li class="nav-item">
						<a class="nav-link" href="/profile">Profile</a>
					</li>
					<li class="nav-item">
						<button class="btn btn-outline-light btn-sm ms-2" onclick={handleLock}>Lock</button>
					</li>
				{:else}
					<li class="nav-item">
						<a class="nav-link" href="/unlock">Unlock</a>
					</li>
					<li class="nav-item">
						<a class="nav-link" href="/enlist">Enlist</a>
					</li>
				{/if}
			</ul>
		</div>
	</div>
</nav>

<main class="container py-4">
	{@render children()}
</main>

<style>
	/* Additional custom styles to complement Bootstrap */
	:global(body) {
		background-color: #f8f9fa;
	}
</style>
