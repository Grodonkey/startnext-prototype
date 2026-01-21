const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint, options = {}) {
	const token = localStorage.getItem('token');

	const headers = {
		'Content-Type': 'application/json',
		...options.headers
	};

	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	const response = await fetch(`${API_URL}${endpoint}`, {
		...options,
		headers
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
		throw new Error(error.detail || 'An error occurred');
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
		localStorage.setItem('token', response.access_token);
		localStorage.setItem('user', JSON.stringify(response.user));
	}

	return response;
}

export async function logout() {
	await apiRequest('/api/auth/logout', { method: 'POST' });
	localStorage.removeItem('token');
	localStorage.removeItem('user');
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
