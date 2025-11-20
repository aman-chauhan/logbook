<script lang="ts">
	import { goto } from '$app/navigation';
	import { getChronicle, deleteEntry, type Entry } from '$lib/api';
	import { auth } from '$lib/stores/auth';

	let entries = $state<Entry[]>([]);
	let error = $state('');
	let loading = $state(true);

	// Redirect if not authenticated
	$effect(() => {
		if (!$auth.isAuthenticated) {
			goto('/unlock');
		} else {
			loadChronicle();
		}
	});

	async function loadChronicle() {
		loading = true;
		error = '';

		const result = await getChronicle({
			username: $auth.username,
			password: $auth.password
		});

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		entries = result.data || [];
		loading = false;
	}

	async function handleDelete(entryId: string) {
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

		// Remove from local list
		entries = entries.filter((e) => e.id !== entryId);
	}

	function formatDate(isoDate: string): string {
		return new Date(isoDate).toLocaleString();
	}
</script>

<div class="mb-4">
	<h1>Chronicle</h1>
	<p class="lead text-muted">Your documented journey.</p>
</div>

{#if error}
	<div class="alert alert-danger border-start border-4 border-danger">{error}</div>
{/if}

{#if loading}
	<div class="card shadow-sm">
		<div class="card-body text-center py-5">
			<div class="spinner-border text-primary" role="status">
				<span class="visually-hidden">Loading...</span>
			</div>
			<p class="mt-3 text-muted mb-0">Loading your entries...</p>
		</div>
	</div>
{:else if entries.length === 0}
	<div class="card shadow-sm border-start border-4 border-info">
		<div class="card-body p-4">
			<div class="alert alert-info border-0 mb-0">
				No entries yet. <a href="/entries/new" class="fw-semibold text-decoration-none"
					>Create your first entry</a
				>.
			</div>
		</div>
	</div>
{:else}
	{#each entries as entry}
		<div class="card mb-3 shadow-sm border-start border-3 border-primary">
			<div class="card-body p-4">
				<p class="card-text mb-3">{entry.attributes.content}</p>
				<div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
					<div class="text-muted small">
						<span>{formatDate(entry.attributes.createdAt)}</span>
						{#if entry.attributes.visibility === 'private'}
							<span class="badge bg-secondary ms-2 rounded-pill">Private</span>
						{/if}
					</div>
					<div class="d-flex gap-2">
						<a href="/entries/{entry.id}" class="btn btn-sm btn-outline-primary rounded shadow-sm"
							>Edit</a
						>
						<button
							class="btn btn-sm btn-outline-danger rounded shadow-sm"
							onclick={() => handleDelete(entry.id)}
						>
							Delete
						</button>
					</div>
				</div>
			</div>
		</div>
	{/each}
{/if}
