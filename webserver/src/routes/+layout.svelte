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

<nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm">
	<div class="container">
		<a class="navbar-brand fw-bold text-primary" href="/">Logbook</a>
		<button
			class="navbar-toggler border-0"
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
			<ul class="navbar-nav ms-auto gap-2">
				{#if $auth.isAuthenticated}
					<li class="nav-item">
						<a class="nav-link px-3 py-2 rounded border border-primary text-primary" href="/chronicle">Chronicle</a>
					</li>
					<li class="nav-item">
						<a class="nav-link px-3 py-2 rounded border border-success text-success" href="/entries/new">New Entry</a>
					</li>
					<li class="nav-item">
						<a class="nav-link px-3 py-2 rounded border border-secondary text-secondary" href="/profile">Profile</a>
					</li>
					<li class="nav-item">
						<button class="btn btn-outline-danger btn-sm rounded" onclick={handleLock}>Lock</button>
					</li>
				{:else}
					<li class="nav-item">
						<a class="nav-link px-3 py-2 rounded border border-primary text-primary" href="/unlock">Unlock</a>
					</li>
					<li class="nav-item">
						<a class="nav-link px-3 py-2 rounded border border-success text-success" href="/enlist">Enlist</a>
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
	/* Paper-like aesthetic with soft shadows and rounded edges */
	:global(body) {
		background-color: #f5f5f5;
		color: #333;
	}

	/* Enhance cards with paper-like appearance */
	:global(.card) {
		border: none;
		border-radius: 0.5rem;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
		transition: box-shadow 0.2s ease;
	}

	:global(.card:hover) {
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
	}

	/* Soft shadows for alerts */
	:global(.alert) {
		border-radius: 0.5rem;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
		border: none;
	}

	/* Button refinements */
	:global(.btn) {
		border-radius: 0.375rem;
		transition: all 0.15s ease;
	}

	/* Form controls with subtle styling */
	:global(.form-control),
	:global(.form-select) {
		border-radius: 0.375rem;
		border: 1px solid #dee2e6;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
	}

	:global(.form-control:focus),
	:global(.form-select:focus) {
		box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15);
	}

	/* Nav link hover effect */
	:global(.nav-link) {
		transition: all 0.15s ease;
	}

	:global(.nav-link:hover) {
		background-color: rgba(0, 0, 0, 0.02);
	}
</style>
