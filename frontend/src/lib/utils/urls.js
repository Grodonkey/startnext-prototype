/**
 * URL utility functions for handling API URLs
 */
import { API_URL } from '$lib/api';

/**
 * Get full image URL from a relative path
 * @param {string} imagePath - Relative or absolute image path
 * @returns {string} Full image URL
 */
export function getImageUrl(imagePath) {
	if (!imagePath) return '';
	if (imagePath.startsWith('http')) return imagePath;
	return `${API_URL}${imagePath}`;
}

/**
 * Get full avatar URL from a relative path
 * @param {string} avatarPath - Relative or absolute avatar path
 * @returns {string} Full avatar URL
 */
export function getAvatarUrl(avatarPath) {
	if (!avatarPath) return '';
	if (avatarPath.startsWith('http')) return avatarPath;
	return `${API_URL}${avatarPath}`;
}
