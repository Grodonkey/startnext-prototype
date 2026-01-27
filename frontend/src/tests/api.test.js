import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiRequest, isAuthenticated, isAdmin, getStoredUser } from '$lib/api';

describe('API Utility Functions', () => {
	beforeEach(() => {
		// Clear localStorage before each test
		localStorage.clear();
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.resetAllMocks();
	});

	describe('isAuthenticated', () => {
		it('returns false when no token is stored', () => {
			expect(isAuthenticated()).toBe(false);
		});

		it('returns true when token is stored', () => {
			localStorage.setItem('token', 'test-token');
			expect(isAuthenticated()).toBe(true);
		});
	});

	describe('isAdmin', () => {
		it('returns false when no user is stored', () => {
			expect(isAdmin()).toBe(false);
		});

		it('returns false when user is not admin', () => {
			localStorage.setItem('user', JSON.stringify({ email: 'user@example.com', is_admin: false }));
			expect(isAdmin()).toBe(false);
		});

		it('returns true when user is admin', () => {
			localStorage.setItem('user', JSON.stringify({ email: 'admin@example.com', is_admin: true }));
			expect(isAdmin()).toBe(true);
		});
	});

	describe('getStoredUser', () => {
		it('returns null when no user is stored', () => {
			expect(getStoredUser()).toBe(null);
		});

		it('returns user object when stored', () => {
			const user = { email: 'test@example.com', full_name: 'Test User' };
			localStorage.setItem('user', JSON.stringify(user));
			expect(getStoredUser()).toEqual(user);
		});
	});

	describe('apiRequest', () => {
		it('includes Authorization header when token exists', async () => {
			localStorage.setItem('token', 'test-token');

			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ data: 'test' })
			});

			await apiRequest('/api/test');

			expect(fetch).toHaveBeenCalledWith(
				expect.stringContaining('/api/test'),
				expect.objectContaining({
					headers: expect.objectContaining({
						Authorization: 'Bearer test-token'
					})
				})
			);
		});

		it('does not include Authorization header when no token', async () => {
			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ data: 'test' })
			});

			await apiRequest('/api/test');

			const callArgs = fetch.mock.calls[0][1];
			expect(callArgs.headers.Authorization).toBeUndefined();
		});

		it('returns null for 204 No Content response', async () => {
			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				status: 204
			});

			const result = await apiRequest('/api/test', { method: 'DELETE' });
			expect(result).toBeNull();
		});

		it('throws error for non-ok responses', async () => {
			global.fetch = vi.fn().mockResolvedValue({
				ok: false,
				status: 400,
				json: () => Promise.resolve({ detail: 'Bad request' })
			});

			await expect(apiRequest('/api/test')).rejects.toThrow('Bad request');
		});
	});
});
