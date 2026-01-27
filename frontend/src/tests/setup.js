import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock SvelteKit's $app/environment
vi.mock('$app/environment', () => ({
	browser: true,
	dev: true,
	building: false
}));

// Mock SvelteKit's $app/navigation
vi.mock('$app/navigation', () => ({
	goto: vi.fn(),
	invalidate: vi.fn(),
	invalidateAll: vi.fn(),
	afterNavigate: vi.fn(),
	beforeNavigate: vi.fn()
}));

// Mock SvelteKit's $app/stores
vi.mock('$app/stores', () => {
	const page = {
		subscribe: vi.fn((fn) => {
			fn({ url: new URL('http://localhost'), params: {} });
			return () => {};
		})
	};
	return {
		page,
		navigating: { subscribe: vi.fn() },
		updated: { subscribe: vi.fn() }
	};
});

// Mock fetch for API calls
global.fetch = vi.fn();
