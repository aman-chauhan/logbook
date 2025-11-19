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

<h1>Profile</h1>

{#if $auth.isAuthenticated}
	<p>Manage your Scribe profile.</p>

	{#if error}
		<p class="error">{error}</p>
	{/if}

	{#if success}
		<p class="success">{success}</p>
	{/if}

	<h2>Amend Profile</h2>

	<form onsubmit={handleAmend}>
		<label>
			Username
			<input type="text" value={$auth.scribe?.attributes.username} disabled />
			<small>Username cannot be changed</small>
		</label>

		<label>
			Email
			<input type="email" bind:value={email} required />
		</label>

		<label>
			Bio
			<textarea bind:value={bio} maxlength="500" placeholder="Tell us about yourself..."></textarea>
		</label>

		<label>
			New Password (leave blank to keep current)
			<input type="password" bind:value={newPassword} minlength="6" />
		</label>

		{#if newPassword}
			<label>
				Confirm New Password
				<input type="password" bind:value={confirmPassword} required />
			</label>
		{/if}

		<button type="submit" disabled={loading}>
			{loading ? 'Saving...' : 'Save Changes'}
		</button>
	</form>

	<h2>Retire Account</h2>

	<p>Permanently delete your account and all entries. This cannot be undone.</p>

	{#if showRetireConfirm}
		<p class="error">
			<strong>Are you sure?</strong> This will permanently delete your account and all entries.
		</p>
		<div style="display: flex; gap: 0.5rem;">
			<button class="danger" onclick={handleRetire} disabled={loading}>
				{loading ? 'Retiring...' : 'Yes, Retire My Account'}
			</button>
			<button onclick={() => (showRetireConfirm = false)}>Cancel</button>
		</div>
	{:else}
		<button class="danger" onclick={handleRetire}>Retire Account</button>
	{/if}
{/if}

<style>
	small {
		font-size: 0.75rem;
		color: #666;
	}

	h2 {
		margin-top: 2rem;
	}

	button {
		padding: 0.5rem 1rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		cursor: pointer;
		background: #eee;
	}

	button:hover {
		background: #ddd;
	}
</style>
