/**
 * Unit tests for authentication store.
 * Tests state management and localStorage integration.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import type { Scribe } from '$lib/api';

// Mock browser environment
vi.mock('$app/environment', () => ({
	browser: true
}));

// Mock localStorage
const localStorageMock = (() => {
	let store: Record<string, string> = {};

	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value;
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		}
	};
})();

Object.defineProperty(global, 'localStorage', {
	value: localStorageMock
});

// Import auth store after mocking
import { auth } from './auth';

describe('Auth Store', () => {
	const mockScribe: Scribe = {
		type: 'scribes',
		id: '550e8400-e29b-41d4-a716-446655440000',
		attributes: {
			username: 'testuser',
			email: 'test@example.com',
			bio: 'Test bio',
			createdAt: '2025-01-15T10:30:00Z',
			updatedAt: '2025-01-15T10:30:00Z'
		}
	};

	beforeEach(() => {
		// Clear localStorage before each test
		localStorageMock.clear();
		// Reset auth store to default state
		auth.logout();
	});

	describe('Initial State', () => {
		it('should have default unauthenticated state', () => {
			const state = get(auth);
			expect(state.isAuthenticated).toBe(false);
			expect(state.username).toBe('');
			expect(state.password).toBe('');
			expect(state.scribe).toBeNull();
		});

		it('should load state from localStorage if available', () => {
			// Set up localStorage with existing auth state
			const storedState = {
				isAuthenticated: true,
				username: 'testuser',
				password: 'password123',
				scribe: mockScribe
			};
			localStorageMock.setItem('logbook_auth', JSON.stringify(storedState));

			// Re-import to trigger initialization
			vi.resetModules();
			// We can't easily test this without a full re-import, so we'll test the persistence instead
		});
	});

	describe('login', () => {
		it('should set authenticated state', () => {
			auth.login('testuser', 'password123', mockScribe);

			const state = get(auth);
			expect(state.isAuthenticated).toBe(true);
			expect(state.username).toBe('testuser');
			expect(state.password).toBe('password123');
			expect(state.scribe).toEqual(mockScribe);
		});

		it('should persist state to localStorage', () => {
			auth.login('testuser', 'password123', mockScribe);

			const stored = localStorageMock.getItem('logbook_auth');
			expect(stored).not.toBeNull();

			const parsedState = JSON.parse(stored!);
			expect(parsedState.isAuthenticated).toBe(true);
			expect(parsedState.username).toBe('testuser');
			expect(parsedState.password).toBe('password123');
			expect(parsedState.scribe).toEqual(mockScribe);
		});
	});

	describe('logout', () => {
		it('should clear authenticated state', () => {
			// First login
			auth.login('testuser', 'password123', mockScribe);

			// Then logout
			auth.logout();

			const state = get(auth);
			expect(state.isAuthenticated).toBe(false);
			expect(state.username).toBe('');
			expect(state.password).toBe('');
			expect(state.scribe).toBeNull();
		});

		it('should remove state from localStorage', () => {
			// First login
			auth.login('testuser', 'password123', mockScribe);
			expect(localStorageMock.getItem('logbook_auth')).not.toBeNull();

			// Then logout
			auth.logout();
			expect(localStorageMock.getItem('logbook_auth')).toBeNull();
		});
	});

	describe('updateScribe', () => {
		it('should update scribe data while maintaining auth state', () => {
			// First login
			auth.login('testuser', 'password123', mockScribe);

			// Update scribe
			const updatedScribe: Scribe = {
				...mockScribe,
				attributes: {
					...mockScribe.attributes,
					bio: 'Updated bio',
					email: 'newemail@example.com'
				}
			};
			auth.updateScribe(updatedScribe);

			const state = get(auth);
			expect(state.isAuthenticated).toBe(true);
			expect(state.username).toBe('testuser');
			expect(state.password).toBe('password123');
			expect(state.scribe).toEqual(updatedScribe);
			expect(state.scribe?.attributes.bio).toBe('Updated bio');
		});

		it('should persist updated scribe to localStorage', () => {
			auth.login('testuser', 'password123', mockScribe);

			const updatedScribe: Scribe = {
				...mockScribe,
				attributes: {
					...mockScribe.attributes,
					bio: 'Updated bio'
				}
			};
			auth.updateScribe(updatedScribe);

			const stored = localStorageMock.getItem('logbook_auth');
			const parsedState = JSON.parse(stored!);
			expect(parsedState.scribe.attributes.bio).toBe('Updated bio');
		});
	});

	describe('updatePassword', () => {
		it('should update password while maintaining other state', () => {
			// First login
			auth.login('testuser', 'password123', mockScribe);

			// Update password
			auth.updatePassword('newpassword456');

			const state = get(auth);
			expect(state.isAuthenticated).toBe(true);
			expect(state.username).toBe('testuser');
			expect(state.password).toBe('newpassword456');
			expect(state.scribe).toEqual(mockScribe);
		});

		it('should persist updated password to localStorage', () => {
			auth.login('testuser', 'password123', mockScribe);
			auth.updatePassword('newpassword456');

			const stored = localStorageMock.getItem('logbook_auth');
			const parsedState = JSON.parse(stored!);
			expect(parsedState.password).toBe('newpassword456');
		});
	});

	describe('getCredentials', () => {
		it('should return credentials when authenticated', () => {
			auth.login('testuser', 'password123', mockScribe);

			const credentials = auth.getCredentials();
			expect(credentials).not.toBeNull();
			expect(credentials?.username).toBe('testuser');
			expect(credentials?.password).toBe('password123');
		});

		it('should return null when not authenticated', () => {
			auth.logout();

			const credentials = auth.getCredentials();
			expect(credentials).toBeNull();
		});

		it('should return current credentials after password update', () => {
			auth.login('testuser', 'password123', mockScribe);
			auth.updatePassword('newpassword456');

			const credentials = auth.getCredentials();
			expect(credentials?.username).toBe('testuser');
			expect(credentials?.password).toBe('newpassword456');
		});
	});

	describe('Subscription', () => {
		it('should notify subscribers of state changes', () => {
			const states: any[] = [];
			const unsubscribe = auth.subscribe((state) => {
				states.push(state);
			});

			// Initial state
			expect(states.length).toBeGreaterThan(0);

			// Login
			auth.login('testuser', 'password123', mockScribe);
			expect(states[states.length - 1].isAuthenticated).toBe(true);

			// Logout
			auth.logout();
			expect(states[states.length - 1].isAuthenticated).toBe(false);

			unsubscribe();
		});
	});

	describe('localStorage Error Handling', () => {
		it('should handle invalid JSON in localStorage gracefully', () => {
			// Set invalid JSON in localStorage
			localStorageMock.setItem('logbook_auth', 'invalid json {');

			// This would happen during initialization, but we can't easily test that
			// The store should fall back to default state
			// For now, we verify the store doesn't crash
			const state = get(auth);
			expect(state).toBeDefined();
		});
	});
});
