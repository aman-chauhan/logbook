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

<p class="lead">Join Logbook as a new Scribe.</p>

{#if error}
	<div class="alert alert-danger">{error}</div>
{/if}

<form onsubmit={handleSubmit} class="col-md-6">
	<div class="mb-3">
		<label for="username" class="form-label">Username</label>
		<input
			type="text"
			class="form-control"
			id="username"
			bind:value={username}
			required
			minlength="3"
			maxlength="64"
		/>
	</div>

	<div class="mb-3">
		<label for="email" class="form-label">Email</label>
		<input type="email" class="form-control" id="email" bind:value={email} required />
	</div>

	<div class="mb-3">
		<label for="password" class="form-label">Password</label>
		<input
			type="password"
			class="form-control"
			id="password"
			bind:value={password}
			required
			minlength="6"
		/>
	</div>

	<div class="mb-3">
		<label for="confirmPassword" class="form-label">Confirm Password</label>
		<input
			type="password"
			class="form-control"
			id="confirmPassword"
			bind:value={confirmPassword}
			required
		/>
	</div>

	<button type="submit" class="btn btn-primary" disabled={loading}>
		{loading ? 'Enlisting...' : 'Enlist'}
	</button>
</form>

<p class="mt-3">Already have an account? <a href="/unlock">Unlock</a> your logbook.</p>
