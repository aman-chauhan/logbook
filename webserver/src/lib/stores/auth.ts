/**
 * Authentication store for managing user session state.
 * Stores credentials in memory and persists to localStorage.
 */

import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import type { Scribe } from '$lib/api';

export interface AuthState {
	isAuthenticated: boolean;
	username: string;
	password: string;
	scribe: Scribe | null;
}

const defaultState: AuthState = {
	isAuthenticated: false,
	username: '',
	password: '',
	scribe: null
};

function createAuthStore() {
	// Load initial state from localStorage if in browser
	let initialState = defaultState;
	if (browser) {
		const stored = localStorage.getItem('logbook_auth');
		if (stored) {
			try {
				initialState = JSON.parse(stored);
			} catch {
				initialState = defaultState;
			}
		}
	}

	const store = writable<AuthState>(initialState);
	const { subscribe, set, update } = store;

	return {
		subscribe,

		/**
		 * Set authenticated state after successful unlock
		 */
		login: (username: string, password: string, scribe: Scribe) => {
			const state: AuthState = {
				isAuthenticated: true,
				username,
				password,
				scribe
			};
			set(state);
			if (browser) {
				localStorage.setItem('logbook_auth', JSON.stringify(state));
			}
		},

		/**
		 * Clear authentication state on lock
		 */
		logout: () => {
			set(defaultState);
			if (browser) {
				localStorage.removeItem('logbook_auth');
			}
		},

		/**
		 * Update scribe data (after profile changes)
		 */
		updateScribe: (scribe: Scribe) => {
			update((state) => {
				const newState = { ...state, scribe };
				if (browser) {
					localStorage.setItem('logbook_auth', JSON.stringify(newState));
				}
				return newState;
			});
		},

		/**
		 * Update password in store (after password change)
		 */
		updatePassword: (newPassword: string) => {
			update((state) => {
				const newState = { ...state, password: newPassword };
				if (browser) {
					localStorage.setItem('logbook_auth', JSON.stringify(newState));
				}
				return newState;
			});
		},

		/**
		 * Get current auth credentials
		 */
		getCredentials: (): { username: string; password: string } | null => {
			const state = get(store);
			if (state.isAuthenticated) {
				return { username: state.username, password: state.password };
			}
			return null;
		}
	};
}

export const auth = createAuthStore();
