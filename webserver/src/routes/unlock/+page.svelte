<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { unlock } from '$lib/api';
	import { auth } from '$lib/stores/auth';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	// Check if user just enlisted
	const enlisted = $page.url.searchParams.get('enlisted');

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		loading = true;

		const result = await unlock(username, password);

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		if (result.data) {
			auth.login(username, password, result.data);
			goto('/chronicle');
		}
	}
</script>

<h1>Unlock</h1>

<p class="lead">Access your logbook.</p>

{#if enlisted}
	<div class="alert alert-success">Successfully enlisted! Please unlock your logbook.</div>
{/if}

{#if error}
	<div class="alert alert-danger">{error}</div>
{/if}

<form onsubmit={handleSubmit} class="col-md-6">
	<div class="mb-3">
		<label for="username" class="form-label">Username</label>
		<input type="text" class="form-control" id="username" bind:value={username} required />
	</div>

	<div class="mb-3">
		<label for="password" class="form-label">Password</label>
		<input type="password" class="form-control" id="password" bind:value={password} required />
	</div>

	<button type="submit" class="btn btn-primary" disabled={loading}>
		{loading ? 'Unlocking...' : 'Unlock'}
	</button>
</form>

<p class="mt-3">New to Logbook? <a href="/enlist">Enlist</a> as a Scribe.</p>
