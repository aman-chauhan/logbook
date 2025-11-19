<script lang="ts">
	import { goto } from '$app/navigation';
	import { enlist } from '$lib/api';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		loading = true;

		const result = await enlist(username, email, password);

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		// Redirect to unlock page after successful enlistment
		goto('/unlock?enlisted=true');
	}
</script>

<h1>Enlist</h1>

<p>Join Logbook as a new Scribe.</p>

{#if error}
	<p class="error">{error}</p>
{/if}

<form onsubmit={handleSubmit}>
	<label>
		Username
		<input type="text" bind:value={username} required minlength="3" maxlength="64" />
	</label>

	<label>
		Email
		<input type="email" bind:value={email} required />
	</label>

	<label>
		Password
		<input type="password" bind:value={password} required minlength="6" />
	</label>

	<label>
		Confirm Password
		<input type="password" bind:value={confirmPassword} required />
	</label>

	<button type="submit" disabled={loading}>
		{loading ? 'Enlisting...' : 'Enlist'}
	</button>
</form>

<p>Already have an account? <a href="/unlock">Unlock</a> your logbook.</p>
