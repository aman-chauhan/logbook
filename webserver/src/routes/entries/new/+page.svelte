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

<div class="row justify-content-center">
	<div class="col-lg-8">
		<div class="card shadow-sm border-start border-4 border-success">
			<div class="card-body p-4">
				<h1 class="mb-3">New Entry</h1>

				<p class="lead mb-4">Document a new record in your chronicle.</p>

				{#if error}
					<div class="alert alert-danger border-start border-4 border-danger">{error}</div>
				{/if}

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
							placeholder="Write your entry..."
						></textarea>
					</div>

					<div class="mb-4">
						<label for="visibility" class="form-label fw-semibold">Visibility</label>
						<select class="form-select" id="visibility" bind:value={visibility}>
							<option value="public">Public</option>
							<option value="private">Private</option>
						</select>
					</div>

					<div class="d-flex gap-2">
						<button type="submit" class="btn btn-success rounded shadow-sm" disabled={loading}>
							{loading ? 'Creating...' : 'Create Entry'}
						</button>
						<a href="/chronicle" class="btn btn-outline-secondary rounded shadow-sm"
							>Back to Chronicle</a
						>
					</div>
				</form>
			</div>
		</div>
	</div>
</div>
