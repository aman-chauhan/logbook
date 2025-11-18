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

<p>Access your logbook.</p>

{#if enlisted}
	<p class="success">Successfully enlisted! Please unlock your logbook.</p>
{/if}

{#if error}
	<p class="error">{error}</p>
{/if}

<form onsubmit={handleSubmit}>
	<label>
		Username
		<input type="text" bind:value={username} required />
	</label>

	<label>
		Password
		<input type="password" bind:value={password} required />
	</label>

	<button type="submit" disabled={loading}>
		{loading ? 'Unlocking...' : 'Unlock'}
	</button>
</form>

<p>New to Logbook? <a href="/enlist">Enlist</a> as a Scribe.</p>
