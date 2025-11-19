<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getEntry, updateEntry, deleteEntry } from '$lib/api';
	import { auth } from '$lib/stores/auth';

	let content = $state('');
	let visibility = $state('public');
	let error = $state('');
	let success = $state('');
	let loading = $state(true);
	let saving = $state(false);

	const entryId = $page.params.id;

	// Redirect if not authenticated
	$effect(() => {
		if (!$auth.isAuthenticated) {
			goto('/unlock');
		} else {
			loadEntry();
		}
	});

	async function loadEntry() {
		loading = true;
		error = '';

		const result = await getEntry(entryId, {
			username: $auth.username,
			password: $auth.password
		});

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		if (result.data) {
			content = result.data.attributes.content;
			visibility = result.data.attributes.visibility;
		}

		loading = false;
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		success = '';
		saving = true;

		const result = await updateEntry(
			entryId,
			{ content, visibility },
			{
				username: $auth.username,
				password: $auth.password
			}
		);

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			saving = false;
			return;
		}

		success = 'Entry updated successfully';
		saving = false;
	}

	async function handleDelete() {
		if (!confirm('Are you sure you want to delete this entry?')) {
			return;
		}

		const result = await deleteEntry(entryId, {
			username: $auth.username,
			password: $auth.password
		});

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			return;
		}

		goto('/chronicle');
	}
</script>

<h1>Edit Entry</h1>

{#if error}
	<p class="error">{error}</p>
{/if}

{#if success}
	<p class="success">{success}</p>
{/if}

{#if loading}
	<p>Loading...</p>
{:else}
	<form onsubmit={handleSubmit}>
		<label>
			Content
			<textarea bind:value={content} required maxlength="10000"></textarea>
		</label>

		<label>
			Visibility
			<select bind:value={visibility}>
				<option value="public">Public</option>
				<option value="private">Private</option>
			</select>
		</label>

		<button type="submit" disabled={saving}>
			{saving ? 'Saving...' : 'Save Changes'}
		</button>
	</form>

	<div style="margin-top: 2rem;">
		<button class="danger" onclick={handleDelete}>Delete Entry</button>
	</div>
{/if}

<p><a href="/chronicle">Back to Chronicle</a></p>

<style>
	button {
		padding: 0.5rem 1rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		cursor: pointer;
		background: #eee;
	}

	button:hover {
		background: #ddd;
	}
</style>
