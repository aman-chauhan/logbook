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

<h1>Chronicle</h1>

<p class="lead">Your documented journey.</p>

{#if error}
	<div class="alert alert-danger">{error}</div>
{/if}

{#if loading}
	<div class="d-flex justify-content-center">
		<div class="spinner-border text-primary" role="status">
			<span class="visually-hidden">Loading...</span>
		</div>
	</div>
{:else if entries.length === 0}
	<div class="alert alert-info">
		No entries yet. <a href="/entries/new">Create your first entry</a>.
	</div>
{:else}
	{#each entries as entry}
		<div class="card mb-3">
			<div class="card-body">
				<p class="card-text">{entry.attributes.content}</p>
				<div class="text-muted small">
					<span>{formatDate(entry.attributes.createdAt)}</span>
					{#if entry.attributes.visibility === 'private'}
						<span class="badge bg-secondary ms-2">Private</span>
					{/if}
				</div>
				<div class="mt-2">
					<a href="/entries/{entry.id}" class="btn btn-sm btn-outline-secondary me-2">Edit</a>
					<button class="btn btn-sm btn-outline-danger" onclick={() => handleDelete(entry.id)}>
						Delete
					</button>
				</div>
			</div>
		</div>
	{/each}
{/if}
