<script lang="ts">
	import { goto } from '$app/navigation';
	import { amendScribe, retireScribe } from '$lib/api';
	import { auth } from '$lib/stores/auth';

	// Redirect if not authenticated
	$effect(() => {
		if (!$auth.isAuthenticated) {
			goto('/unlock');
		}
	});

	let email = $state($auth.scribe?.attributes.email || '');
	let bio = $state($auth.scribe?.attributes.bio ?? '');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let error = $state('');
	let success = $state('');
	let loading = $state(false);
	let showRetireConfirm = $state(false);

	async function handleAmend(e: Event) {
		e.preventDefault();
		error = '';
		success = '';

		if (newPassword && newPassword !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		loading = true;

		const updates: { email?: string; bio?: string; password?: string } = {};
		if (email !== $auth.scribe?.attributes.email) {
			updates.email = email;
		}
		if (bio !== ($auth.scribe?.attributes.bio ?? '')) {
			updates.bio = bio;
		}
		if (newPassword) {
			updates.password = newPassword;
		}

		if (Object.keys(updates).length === 0) {
			error = 'No changes to save';
			loading = false;
			return;
		}

		const result = await amendScribe($auth.scribe!.id, updates, {
			username: $auth.username,
			password: $auth.password
		});

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		if (result.data) {
			auth.updateScribe(result.data);
			if (newPassword) {
				auth.updatePassword(newPassword);
			}
			success = 'Profile updated successfully';
			newPassword = '';
			confirmPassword = '';
		}

		loading = false;
	}

	async function handleRetire() {
		if (!showRetireConfirm) {
			showRetireConfirm = true;
			return;
		}

		loading = true;

		const result = await retireScribe($auth.scribe!.id, {
			username: $auth.username,
			password: $auth.password
		});

		if (result.errors) {
			error = result.errors.map((e) => e.detail).join(', ');
			loading = false;
			return;
		}

		auth.logout();
		goto('/?retired=true');
	}
</script>

<div class="row justify-content-center">
	<div class="col-lg-8">
		{#if $auth.isAuthenticated}
			<!-- Profile Section -->
			<div class="card shadow-sm border-start border-4 border-secondary mb-4">
				<div class="card-body p-4">
					<h1 class="mb-3">Profile</h1>
					<p class="lead text-muted mb-4">Manage your Scribe profile.</p>

					{#if error}
						<div class="alert alert-danger border-start border-4 border-danger">{error}</div>
					{/if}

					{#if success}
						<div class="alert alert-success border-start border-4 border-success">{success}</div>
					{/if}

					<h2 class="h5 mb-3 fw-semibold">Amend Profile</h2>

					<form onsubmit={handleAmend}>
						<div class="mb-3">
							<label for="username" class="form-label fw-semibold">Username</label>
							<input
								type="text"
								class="form-control"
								id="username"
								value={$auth.scribe?.attributes.username}
								disabled
							/>
							<div class="form-text">Username cannot be changed</div>
						</div>

						<div class="mb-3">
							<label for="email" class="form-label fw-semibold">Email</label>
							<input type="email" class="form-control" id="email" bind:value={email} required />
						</div>

						<div class="mb-3">
							<label for="bio" class="form-label fw-semibold">Bio</label>
							<textarea
								class="form-control"
								id="bio"
								bind:value={bio}
								maxlength="500"
								rows="3"
								placeholder="Tell us about yourself..."
							></textarea>
						</div>

						<div class="mb-3">
							<label for="newPassword" class="form-label fw-semibold"
								>New Password (leave blank to keep current)</label
							>
							<input
								type="password"
								class="form-control"
								id="newPassword"
								bind:value={newPassword}
								minlength="6"
							/>
						</div>

						{#if newPassword}
							<div class="mb-3">
								<label for="confirmPassword" class="form-label fw-semibold"
									>Confirm New Password</label
								>
								<input
									type="password"
									class="form-control"
									id="confirmPassword"
									bind:value={confirmPassword}
									required
								/>
							</div>
						{/if}

						<button type="submit" class="btn btn-primary rounded shadow-sm" disabled={loading}>
							{loading ? 'Saving...' : 'Save Changes'}
						</button>
					</form>
				</div>
			</div>

			<!-- Danger Zone -->
			<div class="card shadow-sm border-start border-4 border-danger">
				<div class="card-body p-4">
					<h2 class="h5 mb-3 fw-semibold text-danger">Danger Zone</h2>

					<p class="text-muted mb-3">
						Permanently delete your account and all entries. This cannot be undone.
					</p>

					{#if showRetireConfirm}
						<div class="alert alert-warning border-start border-4 border-warning">
							<strong>Are you sure?</strong> This will permanently delete your account and all entries.
						</div>
						<div class="d-flex gap-2">
							<button
								class="btn btn-danger rounded shadow-sm"
								onclick={handleRetire}
								disabled={loading}
							>
								{loading ? 'Retiring...' : 'Yes, Retire My Account'}
							</button>
							<button
								class="btn btn-outline-secondary rounded shadow-sm"
								onclick={() => (showRetireConfirm = false)}>Cancel</button
							>
						</div>
					{:else}
						<button class="btn btn-danger rounded shadow-sm" onclick={handleRetire}
							>Retire Account</button
						>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>
