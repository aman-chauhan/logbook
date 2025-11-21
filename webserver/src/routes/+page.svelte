<script lang="ts">
	import { auth } from '$lib/stores/auth';
</script>

<div class="card shadow-sm">
	<div class="card-body p-5">
		<h1 class="mb-4">Welcome to Logbook</h1>

		<p class="lead mb-4">Document your journey with purpose and intention.</p>

		{#if $auth.isAuthenticated}
			<div class="alert alert-info border-start border-4 border-info">
				Welcome back, <strong>{$auth.scribe?.attributes.username}</strong>!
			</div>
			<div class="d-flex gap-2 flex-wrap">
				<a href="/chronicle" class="btn btn-primary rounded shadow-sm">View your Chronicle</a>
				<a href="/entries/new" class="btn btn-outline-success rounded shadow-sm">Create a new Entry</a>
			</div>
		{:else}
			<div class="d-flex gap-2 flex-wrap align-items-center">
				<a href="/enlist" class="btn btn-success rounded shadow-sm">Enlist</a>
				<span class="text-muted">as a new Scribe or</span>
				<a href="/unlock" class="btn btn-primary rounded shadow-sm">Unlock</a>
				<span class="text-muted">your existing logbook.</span>
			</div>
		{/if}
	</div>
</div>
