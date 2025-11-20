<script lang="ts">
	import { auth } from '$lib/stores/auth';
</script>

<h1>Welcome to Logbook</h1>

<p class="lead">Document your journey with purpose and intention.</p>

{#if $auth.isAuthenticated}
	<div class="alert alert-info">
		Welcome back, <strong>{$auth.scribe?.attributes.username}</strong>!
	</div>
	<p>
		<a href="/chronicle" class="btn btn-primary me-2">View your Chronicle</a>
		<a href="/entries/new" class="btn btn-outline-primary">Create a new Entry</a>
	</p>
{:else}
	<p>
		<a href="/enlist" class="btn btn-primary me-2">Enlist</a> as a new Scribe or
		<a href="/unlock" class="btn btn-outline-primary">Unlock</a> your existing logbook.
	</p>
{/if}
