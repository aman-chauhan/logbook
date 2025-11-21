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

<div class="row justify-content-center">
	<div class="col-lg-8">
		<div class="card shadow-sm border-start border-4 border-warning">
			<div class="card-body p-4">
				<h1 class="mb-3">Edit Entry</h1>

				{#if error}
					<div class="alert alert-danger border-start border-4 border-danger">{error}</div>
				{/if}

				{#if success}
					<div class="alert alert-success border-start border-4 border-success">{success}</div>
				{/if}

				{#if loading}
					<div class="text-center py-5">
						<div class="spinner-border text-primary" role="status">
							<span class="visually-hidden">Loading...</span>
						</div>
						<p class="mt-3 text-muted mb-0">Loading entry...</p>
					</div>
				{:else}
					<form onsubmit={handleSubmit}>
						<div class="mb-3">
							<label for="content" class="form-label fw-semibold">Content</label>
							<textarea
								class="form-control"
								id="content"
								bind:value={content}
								required
								maxlength="10000"
								rows="8"
							></textarea>
						</div>

						<div class="mb-4">
							<label for="visibility" class="form-label fw-semibold">Visibility</label>
							<select class="form-select" id="visibility" bind:value={visibility}>
								<option value="public">Public</option>
								<option value="private">Private</option>
							</select>
						</div>

						<div class="d-flex gap-2 flex-wrap">
							<button type="submit" class="btn btn-primary rounded shadow-sm" disabled={saving}>
								{saving ? 'Saving...' : 'Save Changes'}
							</button>
							<a href="/chronicle" class="btn btn-outline-secondary rounded shadow-sm"
								>Back to Chronicle</a
							>
						</div>
					</form>

					<hr class="my-4" />

					<div>
						<p class="text-muted mb-2">Danger zone</p>
						<button class="btn btn-danger rounded shadow-sm" onclick={handleDelete}
							>Delete Entry</button
						>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
