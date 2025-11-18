<script lang="ts">
	import { auth } from '$lib/stores/auth';
</script>

<h1>Welcome to Logbook</h1>

<p>Document your journey with purpose and intention.</p>

{#if $auth.isAuthenticated}
	<p>Welcome back, <strong>{$auth.scribe?.attributes.username}</strong>!</p>
	<p>
		<a href="/chronicle">View your Chronicle</a> or
		<a href="/entries/new">create a new Entry</a>.
	</p>
{:else}
	<p>
		<a href="/enlist">Enlist</a> as a new Scribe or
		<a href="/unlock">Unlock</a> your existing logbook.
	</p>
{/if}
