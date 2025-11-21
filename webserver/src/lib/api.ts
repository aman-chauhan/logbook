/**
 * API client for communicating with the Logbook Flask backend.
 * Handles all HTTP requests with Basic Auth support.
 */

const API_BASE = '/api';

export interface Scribe {
	type: string;
	id: string;
	attributes: {
		username: string;
		email: string;
		bio: string | null;
		createdAt: string;
		updatedAt: string;
	};
}

export interface Entry {
	type: string;
	id: string;
	attributes: {
		content: string;
		visibility: string;
		createdAt: string;
		updatedAt: string;
		scribeId: string;
		scribeUsername: string;
	};
}

export interface ApiError {
	status: string;
	title: string;
	detail: string;
}

export interface ApiResponse<T> {
	data?: T;
	errors?: ApiError[];
}

/**
 * Create Basic Auth header from credentials
 */
function createAuthHeader(username: string, password: string): string {
	const credentials = btoa(`${username}:${password}`);
	return `Basic ${credentials}`;
}

/**
 * Make an API request with optional Basic Auth
 */
async function apiRequest<T>(
	endpoint: string,
	options: RequestInit = {},
	auth?: { username: string; password: string }
): Promise<ApiResponse<T>> {
	const headers: HeadersInit = {
		'Content-Type': 'application/json',
		Accept: 'application/vnd.api+json',
		...options.headers
	};

	if (auth) {
		(headers as Record<string, string>)['Authorization'] = createAuthHeader(
			auth.username,
			auth.password
		);
	}

	const response = await fetch(`${API_BASE}${endpoint}`, {
		...options,
		headers
	});

	// Handle 204 No Content (for DELETE operations)
	if (response.status === 204) {
		return {};
	}

	const data = await response.json();

	if (!response.ok) {
		return { errors: data.errors || [{ status: String(response.status), title: 'Error', detail: 'An error occurred' }] };
	}

	return data;
}

// Authentication endpoints

export async function enlist(
	username: string,
	email: string,
	password: string
): Promise<ApiResponse<Scribe>> {
	return apiRequest<Scribe>('/auth/enlist', {
		method: 'POST',
		body: JSON.stringify({ username, email, password })
	});
}

export async function unlock(
	username: string,
	password: string
): Promise<ApiResponse<Scribe>> {
	return apiRequest<Scribe>(
		'/auth/unlock',
		{ method: 'POST' },
		{ username, password }
	);
}

export async function lock(
	username: string,
	password: string
): Promise<ApiResponse<null>> {
	return apiRequest<null>(
		'/auth/lock',
		{ method: 'POST' },
		{ username, password }
	);
}

// Scribe endpoints

export async function getScribe(id: string): Promise<ApiResponse<Scribe>> {
	return apiRequest<Scribe>(`/scribes/${id}`);
}

export async function amendScribe(
	id: string,
	updates: { email?: string; bio?: string; password?: string },
	auth: { username: string; password: string }
): Promise<ApiResponse<Scribe>> {
	return apiRequest<Scribe>(
		`/scribes/${id}`,
		{
			method: 'PATCH',
			body: JSON.stringify(updates)
		},
		auth
	);
}

export async function retireScribe(
	id: string,
	auth: { username: string; password: string }
): Promise<ApiResponse<null>> {
	return apiRequest<null>(
		`/scribes/${id}`,
		{ method: 'DELETE' },
		auth
	);
}

// Entry endpoints

export async function createEntry(
	content: string,
	visibility: string,
	auth: { username: string; password: string }
): Promise<ApiResponse<Entry>> {
	return apiRequest<Entry>(
		'/entries',
		{
			method: 'POST',
			body: JSON.stringify({ content, visibility })
		},
		auth
	);
}

export async function getEntry(
	id: string,
	auth?: { username: string; password: string }
): Promise<ApiResponse<Entry>> {
	return apiRequest<Entry>(`/entries/${id}`, {}, auth);
}

export async function updateEntry(
	id: string,
	updates: { content?: string; visibility?: string },
	auth: { username: string; password: string }
): Promise<ApiResponse<Entry>> {
	return apiRequest<Entry>(
		`/entries/${id}`,
		{
			method: 'PATCH',
			body: JSON.stringify(updates)
		},
		auth
	);
}

export async function deleteEntry(
	id: string,
	auth: { username: string; password: string }
): Promise<ApiResponse<null>> {
	return apiRequest<null>(
		`/entries/${id}`,
		{ method: 'DELETE' },
		auth
	);
}

export async function getChronicle(
	auth: { username: string; password: string }
): Promise<ApiResponse<Entry[]>> {
	return apiRequest<Entry[]>('/chronicle', {}, auth);
}
