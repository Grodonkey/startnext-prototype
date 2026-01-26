import { auth } from './stores/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let isRefreshing = false;
let refreshPromise = null;

async function refreshAccessToken() {
	const sessionToken = localStorage.getItem('session_token');
	if (!sessionToken) {
		return null;
	}

	try {
		const response = await fetch(`${API_URL}/api/auth/refresh`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ session_token: sessionToken })
		});

		if (!response.ok) {
			return null;
		}

		const data = await response.json();
		localStorage.setItem('token', data.access_token);
		return data.access_token;
	} catch {
		return null;
	}
}

export async function apiRequest(endpoint, options = {}) {
	const token = localStorage.getItem('token');

	const headers = {
		'Content-Type': 'application/json',
		...options.headers
	};

	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	let response = await fetch(`${API_URL}${endpoint}`, {
		...options,
		headers
	});

	// If unauthorized, try to refresh the token
	if (response.status === 401 && !options._isRetry) {
		// Prevent multiple simultaneous refresh attempts
		if (!isRefreshing) {
			isRefreshing = true;
			refreshPromise = refreshAccessToken();
		}

		const newToken = await refreshPromise;
		isRefreshing = false;
		refreshPromise = null;

		if (newToken) {
			// Retry the original request with new token
			headers['Authorization'] = `Bearer ${newToken}`;
			response = await fetch(`${API_URL}${endpoint}`, {
				...options,
				headers,
				_isRetry: true
			});
		} else {
			// Refresh failed, clear auth state
			auth.clear();
			const error = await response.json().catch(() => ({ detail: 'Session expired' }));
			throw new Error(error.detail || 'Session expired');
		}
	}

	if (!response.ok) {
		if (response.status === 401) {
			auth.clear();
		}
		const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
		throw new Error(error.detail || 'An error occurred');
	}

	// Handle 204 No Content responses
	if (response.status === 204) {
		return null;
	}

	return response.json();
}

export async function register(email, password, fullName) {
	return apiRequest('/api/auth/register', {
		method: 'POST',
		body: JSON.stringify({
			email,
			password,
			full_name: fullName
		})
	});
}

export async function login(email, password, twoFactorCode = null) {
	const response = await apiRequest('/api/auth/login', {
		method: 'POST',
		body: JSON.stringify({
			email,
			password,
			two_factor_code: twoFactorCode
		})
	});

	if (response.access_token) {
		auth.setUser(response.user, response.access_token);
		if (response.session_token) {
			localStorage.setItem('session_token', response.session_token);
		}
	}

	return response;
}

export async function logout() {
	try {
		await apiRequest('/api/auth/logout', { method: 'POST' });
	} finally {
		auth.clear();
		localStorage.removeItem('session_token');
	}
}

export async function getCurrentUser() {
	return apiRequest('/api/auth/me');
}

export async function updateProfile(data) {
	return apiRequest('/api/users/profile', {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

export async function requestPasswordReset(email) {
	return apiRequest('/api/auth/password-reset-request', {
		method: 'POST',
		body: JSON.stringify({ email })
	});
}

export async function confirmPasswordReset(token, newPassword) {
	return apiRequest('/api/auth/password-reset-confirm', {
		method: 'POST',
		body: JSON.stringify({
			token,
			new_password: newPassword
		})
	});
}

// Magic Link functions
export async function requestMagicLink(email) {
	return apiRequest('/api/auth/magic-link/request', {
		method: 'POST',
		body: JSON.stringify({ email })
	});
}

export async function verifyMagicLink(token) {
	const response = await apiRequest('/api/auth/magic-link/verify', {
		method: 'POST',
		body: JSON.stringify({ token })
	});

	if (response.access_token) {
		auth.setUser(response.user, response.access_token);
		if (response.session_token) {
			localStorage.setItem('session_token', response.session_token);
		}
	}

	return response;
}

export async function setup2FA() {
	return apiRequest('/api/2fa/setup', { method: 'POST' });
}

export async function verify2FA(code) {
	return apiRequest('/api/2fa/verify', {
		method: 'POST',
		body: JSON.stringify({ code })
	});
}

export async function disable2FA(code) {
	return apiRequest('/api/2fa/disable', {
		method: 'POST',
		body: JSON.stringify({ code })
	});
}

export async function listUsers(skip = 0, limit = 100) {
	return apiRequest(`/api/admin/users?skip=${skip}&limit=${limit}`);
}

export async function getUser(userId) {
	return apiRequest(`/api/admin/users/${userId}`);
}

export async function updateUser(userId, data) {
	return apiRequest(`/api/admin/users/${userId}`, {
		method: 'PATCH',
		body: JSON.stringify(data)
	});
}

export async function deleteUser(userId) {
	return apiRequest(`/api/admin/users/${userId}`, { method: 'DELETE' });
}

export async function sendTestEmail(email, emailType, userName = null) {
	return apiRequest('/api/admin/test-email', {
		method: 'POST',
		body: JSON.stringify({
			email,
			email_type: emailType,
			user_name: userName
		})
	});
}

export function getStoredUser() {
	const userStr = localStorage.getItem('user');
	return userStr ? JSON.parse(userStr) : null;
}

export function isAuthenticated() {
	return !!localStorage.getItem('token');
}

export function isAdmin() {
	const user = getStoredUser();
	return user?.is_admin || false;
}

// Project functions
export async function suggestSlug(title) {
	return apiRequest(`/api/projects/suggest-slug?title=${encodeURIComponent(title)}`);
}

export async function createProject(data) {
	return apiRequest('/api/projects', {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

export async function listProjects(status = null, skip = 0, limit = 20) {
	let url = `/api/projects?skip=${skip}&limit=${limit}`;
	if (status) {
		url += `&status=${status}`;
	}
	return apiRequest(url);
}

export async function listMyProjects() {
	return apiRequest('/api/projects/my-projects');
}

export async function getProject(slug) {
	return apiRequest(`/api/projects/${slug}`);
}

export async function updateProject(slug, data) {
	return apiRequest(`/api/projects/${slug}`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

export async function deleteProject(slug) {
	return apiRequest(`/api/projects/${slug}`, { method: 'DELETE' });
}

export async function submitProject(slug) {
	return apiRequest(`/api/projects/${slug}/submit`, { method: 'POST' });
}

export async function duplicateProject(slug) {
	return apiRequest(`/api/projects/${slug}/duplicate`, { method: 'POST' });
}

// Admin Project functions
export async function adminListProjects(status = null, projectType = null, skip = 0, limit = 100) {
	let url = `/api/admin/projects?skip=${skip}&limit=${limit}`;
	if (status) {
		url += `&status=${status}`;
	}
	if (projectType) {
		url += `&project_type=${projectType}`;
	}
	return apiRequest(url);
}

export async function adminGetProject(projectId) {
	return apiRequest(`/api/admin/projects/${projectId}`);
}

export async function adminUpdateProject(projectId, data) {
	return apiRequest(`/api/admin/projects/${projectId}`, {
		method: 'PATCH',
		body: JSON.stringify(data)
	});
}

export async function adminDeleteProject(projectId) {
	return apiRequest(`/api/admin/projects/${projectId}`, { method: 'DELETE' });
}

// Featured/Discover functions
export async function listFeaturedProjects(limit = 4) {
	return apiRequest(`/api/projects/featured?limit=${limit}`);
}

export async function listNearGoalProjects(minPercentage = 80, limit = 10) {
	return apiRequest(`/api/projects/near-goal?min_percentage=${minPercentage}&limit=${limit}`);
}

// Public Profile functions
export async function getPublicProfile(profileSlug) {
	return apiRequest(`/api/profiles/${profileSlug}`);
}

export async function getSuccessfulStarters(limit = 4) {
	return apiRequest(`/api/profiles/starters/successful?limit=${limit}`);
}

export async function getAllStarters(skip = 0, limit = 50) {
	return apiRequest(`/api/profiles/starters/all?skip=${skip}&limit=${limit}`);
}
