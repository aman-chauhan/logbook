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

<p>Your documented journey.</p>

{#if error}
	<p class="error">{error}</p>
{/if}

{#if loading}
	<p>Loading...</p>
{:else if entries.length === 0}
	<p>No entries yet. <a href="/entries/new">Create your first entry</a>.</p>
{:else}
	{#each entries as entry}
		<div class="entry">
			<p>{entry.attributes.content}</p>
			<div class="entry-meta">
				<span>{formatDate(entry.attributes.createdAt)}</span>
				{#if entry.attributes.visibility === 'private'}
					<span> &bull; Private</span>
				{/if}
			</div>
			<div class="entry-actions">
				<a href="/entries/{entry.id}">Edit</a>
				<button onclick={() => handleDelete(entry.id)}>Delete</button>
			</div>
		</div>
	{/each}
{/if}
