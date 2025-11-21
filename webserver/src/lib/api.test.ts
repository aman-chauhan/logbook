/**
 * Unit tests for API client module.
 * Tests all API functions with mocked fetch responses.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
	enlist,
	unlock,
	lock,
	getScribe,
	amendScribe,
	retireScribe,
	createEntry,
	getEntry,
	updateEntry,
	deleteEntry,
	getChronicle,
	type Scribe,
	type Entry,
	type ApiError
} from './api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Client', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('Authentication Endpoints', () => {
		it('enlist should create a new scribe', async () => {
			const mockScribe: Scribe = {
				type: 'scribes',
				id: '550e8400-e29b-41d4-a716-446655440000',
				attributes: {
					username: 'testuser',
					email: 'test@example.com',
					bio: null,
					createdAt: '2025-01-15T10:30:00Z',
					updatedAt: '2025-01-15T10:30:00Z'
				}
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: async () => ({ data: mockScribe })
			});

			const result = await enlist('testuser', 'test@example.com', 'password123');

			expect(global.fetch).toHaveBeenCalledWith('/api/auth/enlist', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Accept: 'application/vnd.api+json'
				},
				body: JSON.stringify({
					username: 'testuser',
					email: 'test@example.com',
					password: 'password123'
				})
			});
			expect(result.data).toEqual(mockScribe);
			expect(result.errors).toBeUndefined();
		});

		it('unlock should authenticate a scribe', async () => {
			const mockScribe: Scribe = {
				type: 'scribes',
				id: '550e8400-e29b-41d4-a716-446655440000',
				attributes: {
					username: 'testuser',
					email: 'test@example.com',
					bio: null,
					createdAt: '2025-01-15T10:30:00Z',
					updatedAt: '2025-01-15T10:30:00Z'
				}
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: mockScribe })
			});

			const result = await unlock('testuser', 'password123');

			// Check that Authorization header was set
			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/auth/unlock');
			expect(fetchCall[1].headers.Authorization).toMatch(/^Basic /);
			expect(result.data).toEqual(mockScribe);
		});

		it('lock should clear authentication', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			const result = await lock('testuser', 'password123');

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/auth/lock');
			expect(fetchCall[1].headers.Authorization).toMatch(/^Basic /);
			expect(result).toEqual({});
		});

		it('should handle authentication errors', async () => {
			const mockError: ApiError = {
				status: '401',
				title: 'Invalid Credentials',
				detail: 'The username or password provided is incorrect'
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: false,
				status: 401,
				json: async () => ({ errors: [mockError] })
			});

			const result = await unlock('testuser', 'wrongpassword');

			expect(result.data).toBeUndefined();
			expect(result.errors).toEqual([mockError]);
		});
	});

	describe('Scribe Endpoints', () => {
		it('getScribe should fetch a scribe profile', async () => {
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

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: mockScribe })
			});

			const result = await getScribe('550e8400-e29b-41d4-a716-446655440000');

			expect(global.fetch).toHaveBeenCalledWith(
				'/api/scribes/550e8400-e29b-41d4-a716-446655440000',
				{
					headers: {
						'Content-Type': 'application/json',
						Accept: 'application/vnd.api+json'
					}
				}
			);
			expect(result.data).toEqual(mockScribe);
		});

		it('amendScribe should update scribe profile', async () => {
			const mockScribe: Scribe = {
				type: 'scribes',
				id: '550e8400-e29b-41d4-a716-446655440000',
				attributes: {
					username: 'testuser',
					email: 'newemail@example.com',
					bio: 'Updated bio',
					createdAt: '2025-01-15T10:30:00Z',
					updatedAt: '2025-01-15T10:35:00Z'
				}
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: mockScribe })
			});

			const result = await amendScribe(
				'550e8400-e29b-41d4-a716-446655440000',
				{ email: 'newemail@example.com', bio: 'Updated bio' },
				{ username: 'testuser', password: 'password123' }
			);

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/scribes/550e8400-e29b-41d4-a716-446655440000');
			expect(fetchCall[1].method).toBe('PATCH');
			expect(fetchCall[1].headers.Authorization).toMatch(/^Basic /);
			expect(JSON.parse(fetchCall[1].body)).toEqual({
				email: 'newemail@example.com',
				bio: 'Updated bio'
			});
			expect(result.data).toEqual(mockScribe);
		});

		it('retireScribe should delete scribe account', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			const result = await retireScribe('550e8400-e29b-41d4-a716-446655440000', {
				username: 'testuser',
				password: 'password123'
			});

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/scribes/550e8400-e29b-41d4-a716-446655440000');
			expect(fetchCall[1].method).toBe('DELETE');
			expect(fetchCall[1].headers.Authorization).toMatch(/^Basic /);
			expect(result).toEqual({});
		});

		it('should handle 404 errors for non-existent scribe', async () => {
			const mockError: ApiError = {
				status: '404',
				title: 'Not Found',
				detail: 'Scribe not found'
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: false,
				status: 404,
				json: async () => ({ errors: [mockError] })
			});

			const result = await getScribe('invalid-id');

			expect(result.data).toBeUndefined();
			expect(result.errors).toEqual([mockError]);
		});
	});

	describe('Entry Endpoints', () => {
		const mockEntry: Entry = {
			type: 'entries',
			id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
			attributes: {
				content: 'Test entry content',
				visibility: 'public',
				createdAt: '2025-01-15T10:30:00Z',
				updatedAt: '2025-01-15T10:30:00Z',
				scribeId: '550e8400-e29b-41d4-a716-446655440000',
				scribeUsername: 'testuser'
			}
		};

		it('createEntry should create a new entry', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: async () => ({ data: mockEntry })
			});

			const result = await createEntry('Test entry content', 'public', {
				username: 'testuser',
				password: 'password123'
			});

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/entries');
			expect(fetchCall[1].method).toBe('POST');
			expect(fetchCall[1].headers.Authorization).toMatch(/^Basic /);
			expect(JSON.parse(fetchCall[1].body)).toEqual({
				content: 'Test entry content',
				visibility: 'public'
			});
			expect(result.data).toEqual(mockEntry);
		});

		it('getEntry should fetch an entry without auth', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: mockEntry })
			});

			const result = await getEntry('7c9e6679-7425-40de-944b-e07fc1f90ae7');

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/entries/7c9e6679-7425-40de-944b-e07fc1f90ae7');
			expect(fetchCall[1].headers.Authorization).toBeUndefined();
			expect(result.data).toEqual(mockEntry);
		});

		it('getEntry should fetch an entry with auth for private entries', async () => {
			const privateEntry = { ...mockEntry };
			privateEntry.attributes.visibility = 'private';

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: privateEntry })
			});

			const result = await getEntry('7c9e6679-7425-40de-944b-e07fc1f90ae7', {
				username: 'testuser',
				password: 'password123'
			});

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[1].headers.Authorization).toMatch(/^Basic /);
			expect(result.data).toEqual(privateEntry);
		});

		it('updateEntry should update an entry', async () => {
			const updatedEntry = { ...mockEntry };
			updatedEntry.attributes.content = 'Updated content';

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: updatedEntry })
			});

			const result = await updateEntry(
				'7c9e6679-7425-40de-944b-e07fc1f90ae7',
				{ content: 'Updated content' },
				{ username: 'testuser', password: 'password123' }
			);

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/entries/7c9e6679-7425-40de-944b-e07fc1f90ae7');
			expect(fetchCall[1].method).toBe('PATCH');
			expect(JSON.parse(fetchCall[1].body)).toEqual({ content: 'Updated content' });
			expect(result.data).toEqual(updatedEntry);
		});

		it('deleteEntry should delete an entry', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			const result = await deleteEntry('7c9e6679-7425-40de-944b-e07fc1f90ae7', {
				username: 'testuser',
				password: 'password123'
			});

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/entries/7c9e6679-7425-40de-944b-e07fc1f90ae7');
			expect(fetchCall[1].method).toBe('DELETE');
			expect(result).toEqual({});
		});

		it('getChronicle should fetch all entries for authenticated scribe', async () => {
			const mockEntries: Entry[] = [mockEntry];

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: mockEntries })
			});

			const result = await getChronicle({
				username: 'testuser',
				password: 'password123'
			});

			const fetchCall = (global.fetch as any).mock.calls[0];
			expect(fetchCall[0]).toBe('/api/chronicle');
			expect(fetchCall[1].headers.Authorization).toMatch(/^Basic /);
			expect(result.data).toEqual(mockEntries);
		});

		it('should handle validation errors', async () => {
			const mockError: ApiError = {
				status: '400',
				title: 'Missing Required Field',
				detail: 'The content field is required'
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: false,
				status: 400,
				json: async () => ({ errors: [mockError] })
			});

			const result = await createEntry('', 'public', {
				username: 'testuser',
				password: 'password123'
			});

			expect(result.data).toBeUndefined();
			expect(result.errors).toEqual([mockError]);
		});
	});

	describe('Error Handling', () => {
		it('should handle response without error details', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: false,
				status: 500,
				json: async () => ({})
			});

			const result = await getScribe('some-id');

			expect(result.errors).toEqual([
				{
					status: '500',
					title: 'Error',
					detail: 'An error occurred'
				}
			]);
		});

		it('should handle 204 No Content responses', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			const result = await deleteEntry('some-id', {
				username: 'test',
				password: 'test'
			});

			expect(result).toEqual({});
		});
	});

	describe('Basic Auth Header Creation', () => {
		it('should create proper Basic Auth header', async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({ data: {} })
			});

			await unlock('testuser', 'password123');

			const fetchCall = (global.fetch as any).mock.calls[0];
			const authHeader = fetchCall[1].headers.Authorization;

			// Verify it's a valid Basic auth header
			expect(authHeader).toMatch(/^Basic /);

			// Decode and verify credentials
			const encodedCreds = authHeader.replace('Basic ', '');
			const decodedCreds = atob(encodedCreds);
			expect(decodedCreds).toBe('testuser:password123');
		});
	});
});
