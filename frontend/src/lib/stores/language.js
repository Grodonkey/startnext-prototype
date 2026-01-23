import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { translations } from '$lib/i18n/translations';

function createLanguageStore() {
	const defaultLang = browser ? localStorage.getItem('language') || 'de' : 'de';

	const { subscribe, set } = writable(defaultLang);

	return {
		subscribe,
		set: (lang) => {
			if (browser) {
				localStorage.setItem('language', lang);
				document.documentElement.lang = lang;
			}
			set(lang);
		},
		toggle: () => {
			let currentLang;
			subscribe((value) => (currentLang = value))();
			const newLang = currentLang === 'de' ? 'en' : 'de';
			if (browser) {
				localStorage.setItem('language', newLang);
				document.documentElement.lang = newLang;
			}
			set(newLang);
		}
	};
}

export const language = createLanguageStore();

// Derived store for translations
export const t = derived(language, ($language) => {
	return (key) => {
		return translations[$language]?.[key] || translations['de'][key] || key;
	};
});
