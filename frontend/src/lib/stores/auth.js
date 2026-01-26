import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createAuthStore() {
	const { subscribe, set, update } = writable({
		isAuthenticated: false,
		user: null,
		isAdmin: false
	});

	function checkAuth() {
		if (!browser) return;

		const token = localStorage.getItem('token');
		const userStr = localStorage.getItem('user');

		if (token && userStr) {
			try {
				const user = JSON.parse(userStr);
				set({
					isAuthenticated: true,
					user,
					isAdmin: user?.is_admin || false
				});
			} catch {
				clear();
			}
		} else {
			clear();
		}
	}

	function setUser(user, token) {
		if (browser) {
			localStorage.setItem('token', token);
			localStorage.setItem('user', JSON.stringify(user));
		}
		set({
			isAuthenticated: true,
			user,
			isAdmin: user?.is_admin || false
		});
	}

	function clear() {
		if (browser) {
			localStorage.removeItem('token');
			localStorage.removeItem('user');
			localStorage.removeItem('session_token');
		}
		set({
			isAuthenticated: false,
			user: null,
			isAdmin: false
		});
	}

	// Check auth status periodically (for token expiry)
	if (browser) {
		checkAuth();
		setInterval(checkAuth, 60000); // Check every minute
	}

	return {
		subscribe,
		checkAuth,
		setUser,
		clear
	};
}

export const auth = createAuthStore();
