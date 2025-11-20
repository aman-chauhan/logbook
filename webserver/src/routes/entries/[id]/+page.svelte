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
	<div class="alert alert-danger">{error}</div>
{/if}

{#if success}
	<div class="alert alert-success">{success}</div>
{/if}

{#if loading}
	<div class="d-flex justify-content-center">
		<div class="spinner-border text-primary" role="status">
			<span class="visually-hidden">Loading...</span>
		</div>
	</div>
{:else}
	<form onsubmit={handleSubmit} class="col-md-8">
		<div class="mb-3">
			<label for="content" class="form-label">Content</label>
			<textarea
				class="form-control"
				id="content"
				bind:value={content}
				required
				maxlength="10000"
				rows="6"
			></textarea>
		</div>

		<div class="mb-3">
			<label for="visibility" class="form-label">Visibility</label>
			<select class="form-select" id="visibility" bind:value={visibility}>
				<option value="public">Public</option>
				<option value="private">Private</option>
			</select>
		</div>

		<button type="submit" class="btn btn-primary" disabled={saving}>
			{saving ? 'Saving...' : 'Save Changes'}
		</button>
	</form>

	<div class="mt-4">
		<button class="btn btn-danger" onclick={handleDelete}>Delete Entry</button>
	</div>
{/if}

<p class="mt-3"><a href="/chronicle">Back to Chronicle</a></p>
