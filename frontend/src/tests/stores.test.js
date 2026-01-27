import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';

// Mock localStorage before importing auth store
const localStorageMock = {
	store: {},
	getItem: vi.fn((key) => localStorageMock.store[key] || null),
	setItem: vi.fn((key, value) => {
		localStorageMock.store[key] = value;
	}),
	removeItem: vi.fn((key) => {
		delete localStorageMock.store[key];
	}),
	clear: vi.fn(() => {
		localStorageMock.store = {};
	})
};

Object.defineProperty(global, 'localStorage', {
	value: localStorageMock,
	writable: true
});

// Import after mocking localStorage
import { auth } from '$lib/stores/auth';

describe('Auth Store', () => {
	beforeEach(() => {
		localStorageMock.clear();
		localStorageMock.getItem.mockClear();
		localStorageMock.setItem.mockClear();
		localStorageMock.removeItem.mockClear();
	});

	it('initializes with null user when not authenticated', () => {
		const state = get(auth);
		expect(state.user).toBe(null);
	});

	it('setUser updates the store and localStorage', () => {
		const testUser = { id: 1, email: 'test@example.com' };
		const testToken = 'test-token';

		auth.setUser(testUser, testToken);

		const state = get(auth);
		expect(state.user).toEqual(testUser);
		expect(state.isAuthenticated).toBe(true);
		expect(localStorageMock.setItem).toHaveBeenCalledWith('token', testToken);
		expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(testUser));
	});

	it('clear removes user and token', () => {
		auth.setUser({ id: 1 }, 'token');
		auth.clear();

		const state = get(auth);
		expect(state.user).toBe(null);
		expect(state.isAuthenticated).toBe(false);
		expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
		expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
	});
});
