/**
 * Central export for all utility functions
 */

// Formatting utilities
export {
	formatCurrency,
	calculateProgress,
	formatDate,
	formatDateShort,
	getInitials,
	formatProjectCount
} from './formatting.js';

// Styling utilities
export {
	getStatusColor,
	getProjectTypeColor,
	getProjectTypeColorLight,
	getProjectTypeButtonClass,
	getProjectTypeAccentColor,
	getSortIcon
} from './styling.js';

// URL utilities
export {
	getImageUrl,
	getAvatarUrl
} from './urls.js';
