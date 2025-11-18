<script lang="ts">
	import { goto } from '$app/navigation';
	import { createEntry } from '$lib/api';
	import { auth } from '$lib/stores/auth';

	// Redirect if not authenticated
	$effect(() => {
		if (!$auth.isAuthenticated) {
			goto('/unlock');
		}
	});

	let content = $state('');
	let visibility = $state('public');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		loading = true;

		const result = await createEntry(content, visibility, {
			username: $auth.username,
			password: $auth.password
		});

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		goto('/chronicle');
	}
</script>

<h1>New Entry</h1>

<p>Document a new record in your chronicle.</p>

{#if error}
	<p class="error">{error}</p>
{/if}

<form onsubmit={handleSubmit}>
	<label>
		Content
		<textarea bind:value={content} required maxlength="10000" placeholder="Write your entry..."></textarea>
	</label>

	<label>
		Visibility
		<select bind:value={visibility}>
			<option value="public">Public</option>
			<option value="private">Private</option>
		</select>
	</label>

	<button type="submit" disabled={loading}>
		{loading ? 'Creating...' : 'Create Entry'}
	</button>
</form>

<p><a href="/chronicle">Back to Chronicle</a></p>
