<script lang="ts">
	import { goto } from '$app/navigation';
	import { enlist } from '$lib/api';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		loading = true;

		const result = await enlist(username, email, password);

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		// Redirect to unlock page after successful enlistment
		goto('/unlock?enlisted=true');
	}
</script>

<div class="row justify-content-center">
	<div class="col-md-6">
		<div class="card shadow-sm">
			<div class="card-body p-4">
				<h1 class="mb-3">Enlist</h1>

				<p class="lead mb-4">Join Logbook as a new Scribe.</p>

				{#if error}
					<div class="alert alert-danger border-start border-4 border-danger">{error}</div>
				{/if}

				<form onsubmit={handleSubmit}>
					<div class="mb-3">
						<label for="username" class="form-label fw-semibold">Username</label>
						<input
							type="text"
							class="form-control"
							id="username"
							bind:value={username}
							required
							minlength="3"
							maxlength="64"
						/>
					</div>

					<div class="mb-3">
						<label for="email" class="form-label fw-semibold">Email</label>
						<input type="email" class="form-control" id="email" bind:value={email} required />
					</div>

					<div class="mb-3">
						<label for="password" class="form-label fw-semibold">Password</label>
						<input
							type="password"
							class="form-control"
							id="password"
							bind:value={password}
							required
							minlength="6"
						/>
					</div>

					<div class="mb-3">
						<label for="confirmPassword" class="form-label fw-semibold">Confirm Password</label>
						<input
							type="password"
							class="form-control"
							id="confirmPassword"
							bind:value={confirmPassword}
							required
						/>
					</div>

					<button type="submit" class="btn btn-success w-100 rounded shadow-sm" disabled={loading}>
						{loading ? 'Enlisting...' : 'Enlist'}
					</button>
				</form>

				<hr class="my-4" />

				<p class="text-center text-muted mb-0">
					Already have an account? <a href="/unlock" class="text-decoration-none fw-semibold"
						>Unlock</a
					> your logbook.
				</p>
			</div>
		</div>
	</div>
</div>
