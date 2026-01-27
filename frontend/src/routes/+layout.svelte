<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import { language, t } from '$lib/stores/language';
	import { initStoryblok } from '$lib/storyblok';
	import Avatar from '$lib/components/Avatar.svelte';
	import { getAvatarUrl } from '$lib/utils';

	// Initialize Storyblok
	initStoryblok();

	let mobileMenuOpen = false;

	function closeMobileMenu() {
		mobileMenuOpen = false;
	}

	onMount(() => {
		auth.checkAuth();
	});
</script>

<div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">
	<!-- Safe area spacer for iOS Dynamic Island/Notch -->
	<div class="bg-white dark:bg-gray-800 safe-area-top"></div>
	<nav class="bg-white dark:bg-gray-800 shadow-sm">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<div class="flex items-center space-x-8">
					<a href="/" class="text-xl font-bold text-[#304b50] dark:text-white">
						#startneu
					</a>

					<!-- Main Navigation -->
					<div class="hidden sm:flex items-center space-x-6">
						<a
							href="/vibe"
							class="flex items-center gap-1.5 text-gray-700 dark:text-gray-300 hover:text-[#06E481] dark:hover:text-[#06E481] transition-colors font-medium"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
							</svg>
							{$t('nav.vibe')}
						</a>
						<a
							href="/projects/new"
							class="text-gray-700 dark:text-gray-300 hover:text-[#06E481] dark:hover:text-[#06E481] transition-colors font-medium"
						>
							{$t('nav.startProject')}
						</a>
						<a
							href="/discover"
							class="text-gray-700 dark:text-gray-300 hover:text-[#06E481] dark:hover:text-[#06E481] transition-colors font-medium"
						>
							{$t('nav.discover')}
						</a>
						<a
							href="/community"
							class="text-gray-700 dark:text-gray-300 hover:text-[#06E481] dark:hover:text-[#06E481] transition-colors font-medium"
						>
							{$t('nav.community')}
						</a>
					</div>
				</div>

				<!-- Desktop: Language, Theme, Auth -->
				<div class="hidden sm:flex items-center space-x-4">
					<!-- Language Toggle -->
					<button
						on:click={() => language.toggle()}
						class="p-2 text-gray-600 dark:text-gray-300 hover:text-[#263c40] dark:hover:text-[#33f79f] transition-colors"
						title={$language === 'de' ? 'Switch to English' : 'Auf Deutsch wechseln'}
					>
						<span class="text-sm font-medium">{$language === 'de' ? 'EN' : 'DE'}</span>
					</button>

					<!-- Theme Toggle -->
					<button
						on:click={() => theme.toggle()}
						class="p-2 text-gray-600 dark:text-gray-300 hover:text-[#263c40] dark:hover:text-[#33f79f] transition-colors"
						title={$t('theme.toggle')}
					>
						{#if $theme === 'dark'}
							<!-- Sun Icon -->
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
								/>
							</svg>
						{:else}
							<!-- Moon Icon -->
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
								/>
							</svg>
						{/if}
					</button>

					<div class="h-6 w-px bg-gray-300 dark:bg-gray-600"></div>

					{#if $auth.isAuthenticated}
						<a href="/profile" class="flex items-center">
							<Avatar
								name={$auth.user?.full_name || ''}
								imageUrl={getAvatarUrl($auth.user?.avatar_url)}
								size="sm"
							/>
						</a>
					{:else}
						<a
							href="/login"
							class="text-gray-700 dark:text-gray-300 hover:text-[#263c40] dark:hover:text-[#33f79f]"
							>{$t('nav.login')}</a
						>
					{/if}
				</div>

				<!-- Mobile: Hamburger Button -->
				<button
					on:click={() => mobileMenuOpen = !mobileMenuOpen}
					class="sm:hidden p-2 text-gray-600 dark:text-gray-300 hover:text-[#263c40] dark:hover:text-[#33f79f] transition-colors"
					aria-label="Menu"
				>
					{#if mobileMenuOpen}
						<!-- Close Icon -->
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					{:else}
						<!-- Hamburger Icon -->
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
						</svg>
					{/if}
				</button>
			</div>
		</div>
	</nav>

	<!-- Mobile Menu Slider -->
	{#if mobileMenuOpen}
		<!-- Backdrop -->
		<button
			class="sm:hidden fixed inset-0 bg-black/50 z-40 transition-opacity"
			on:click={closeMobileMenu}
			aria-label="Close menu"
		></button>
	{/if}

	<!-- Slide-in Panel -->
	<div
		class="sm:hidden fixed top-0 right-0 h-full w-72 bg-white dark:bg-gray-800 shadow-xl z-50 transform transition-transform duration-300 ease-in-out {mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'}"
	>
		<!-- Header with Close Button -->
		<div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
			<span class="text-lg font-bold text-[#304b50] dark:text-white">#startneu</span>
			<button
				on:click={closeMobileMenu}
				class="p-2 text-gray-600 dark:text-gray-300 hover:text-[#06E481] transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
				aria-label="Close menu"
			>
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- Menu Content -->
		<div class="p-4 space-y-6 overflow-y-auto h-[calc(100%-64px)]">
			<!-- Profile/Auth Section (at top) -->
			<div class="pb-4 border-b border-gray-200 dark:border-gray-700">
				{#if $auth.isAuthenticated}
					<a
						href="/profile"
						on:click={closeMobileMenu}
						class="flex items-center gap-4 px-3 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
					>
						<Avatar
							name={$auth.user?.full_name || ''}
							imageUrl={getAvatarUrl($auth.user?.avatar_url)}
							size="lg"
						/>
						<div>
							<p class="font-semibold text-[#304b50] dark:text-white">{$auth.user?.full_name || $t('nav.profile')}</p>
							<p class="text-sm text-gray-500 dark:text-gray-400">{$auth.user?.email}</p>
						</div>
					</a>
				{:else}
					<a
						href="/login"
						on:click={closeMobileMenu}
						class="flex items-center gap-3 px-3 py-3 bg-[#06E481] text-[#304b50] font-semibold rounded-lg hover:bg-[#05b667] transition-colors"
					>
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
						</svg>
						{$t('nav.login')}
					</a>
				{/if}
			</div>

			<!-- Main Navigation Links -->
			<nav class="space-y-1">
				<a
					href="/vibe"
					on:click={closeMobileMenu}
					class="flex items-center gap-3 px-3 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-[#06E481] rounded-lg transition-colors font-medium"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
					</svg>
					{$t('nav.vibe')}
				</a>
				<a
					href="/projects/new"
					on:click={closeMobileMenu}
					class="flex items-center gap-3 px-3 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-[#06E481] rounded-lg transition-colors font-medium"
				>
					<span class="text-lg">🚀</span>
					{$t('nav.startProject')}
				</a>
				<a
					href="/discover"
					on:click={closeMobileMenu}
					class="flex items-center gap-3 px-3 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-[#06E481] rounded-lg transition-colors font-medium"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
					</svg>
					{$t('nav.discover')}
				</a>
				<a
					href="/community"
					on:click={closeMobileMenu}
					class="flex items-center gap-3 px-3 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-[#06E481] rounded-lg transition-colors font-medium"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
					{$t('nav.community')}
				</a>
			</nav>

			<!-- Settings -->
			<div class="border-t border-gray-200 dark:border-gray-700 pt-4 space-y-1">
				<p class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
					{$t('theme.toggle')}
				</p>

				<!-- Language Toggle -->
				<button
					on:click={() => language.toggle()}
					class="w-full flex items-center gap-3 px-3 py-3 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<span class="text-sm font-medium">{$language === 'de' ? 'English' : 'Deutsch'}</span>
				</button>

				<!-- Theme Toggle -->
				<button
					on:click={() => theme.toggle()}
					class="w-full flex items-center gap-3 px-3 py-3 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
				>
					{#if $theme === 'dark'}
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
						</svg>
						<span class="text-sm">Light Mode</span>
					{:else}
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
						</svg>
						<span class="text-sm">Dark Mode</span>
					{/if}
				</button>
			</div>
		</div>
	</div>

	<main class="flex-grow">
		<slot />
	</main>

	<!-- Footer -->
	<footer class="bg-[#304b50] text-white mt-auto">
		<!-- Statistics Bar -->
		<div class="bg-[#263c40] py-8">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
					<div>
						<div class="text-3xl md:text-4xl font-bold text-[#06E481]">161.535.269 €</div>
						<div class="text-gray-300 mt-1">{$t('footer.stats.funded')}</div>
					</div>
					<div>
						<div class="text-3xl md:text-4xl font-bold text-[#06E481]">18.201</div>
						<div class="text-gray-300 mt-1">{$t('footer.stats.projects')}</div>
					</div>
					<div>
						<div class="text-3xl md:text-4xl font-bold text-[#06E481]">2.176.000</div>
						<div class="text-gray-300 mt-1">{$t('footer.stats.users')}</div>
					</div>
				</div>
			</div>
		</div>

		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<div class="grid grid-cols-1 md:grid-cols-4 gap-8">
				<!-- Brand -->
				<div class="col-span-1 md:col-span-1">
					<a href="/" class="text-2xl font-bold text-white hover:text-[#06E481] transition-colors">
						#startneu
					</a>
					<p class="mt-4 text-gray-300 text-sm">
						{$t('footer.tagline')}
					</p>
					<!-- Social Links -->
					<div class="flex space-x-4 mt-6">
						<a href="https://instagram.com/startnext" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-[#06E481] transition-colors" title="Instagram">
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
							</svg>
						</a>
						<a href="https://facebook.com/startnext" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-[#06E481] transition-colors" title="Facebook">
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
							</svg>
						</a>
						<a href="https://twitter.com/startnext" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-[#06E481] transition-colors" title="X (Twitter)">
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
							</svg>
						</a>
						<a href="https://linkedin.com/company/startnext" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-[#06E481] transition-colors" title="LinkedIn">
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
							</svg>
						</a>
						<a href="https://youtube.com/@startnext" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-[#06E481] transition-colors" title="YouTube">
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
							</svg>
						</a>
						<a href="https://tiktok.com/@startnext" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-[#06E481] transition-colors" title="TikTok">
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
							</svg>
						</a>
					</div>
				</div>

				<!-- Platform -->
				<div>
					<h3 class="text-sm font-semibold text-[#06E481] uppercase tracking-wider mb-4">
						{$t('footer.platform')}
					</h3>
					<ul class="space-y-3">
						<li><a href="/projects/new" class="text-gray-300 hover:text-white transition-colors">{$t('nav.startProject')}</a></li>
						<li><a href="/discover" class="text-gray-300 hover:text-white transition-colors">{$t('nav.discover')}</a></li>
						<li><a href="/community" class="text-gray-300 hover:text-white transition-colors">{$t('nav.community')}</a></li>
					</ul>
				</div>

				<!-- Support -->
				<div>
					<h3 class="text-sm font-semibold text-[#06E481] uppercase tracking-wider mb-4">
						{$t('footer.support')}
					</h3>
					<ul class="space-y-3">
						<li><a href="/faq" class="text-gray-300 hover:text-white transition-colors">{$t('footer.faq')}</a></li>
						<li><a href="/contact" class="text-gray-300 hover:text-white transition-colors">{$t('footer.contact')}</a></li>
						<li><a href="/help" class="text-gray-300 hover:text-white transition-colors">{$t('footer.help')}</a></li>
					</ul>
				</div>

				<!-- Legal -->
				<div>
					<h3 class="text-sm font-semibold text-[#06E481] uppercase tracking-wider mb-4">
						{$t('footer.legal')}
					</h3>
					<ul class="space-y-3">
						<li><a href="/imprint" class="text-gray-300 hover:text-white transition-colors">{$t('footer.imprint')}</a></li>
						<li><a href="/privacy" class="text-gray-300 hover:text-white transition-colors">{$t('footer.privacy')}</a></li>
						<li><a href="/terms" class="text-gray-300 hover:text-white transition-colors">{$t('footer.terms')}</a></li>
					</ul>
				</div>
			</div>

			<!-- Funding Notice -->
			<div class="mt-10 p-4 bg-[#263c40] rounded-lg">
				<div class="flex items-start gap-4">
					<div class="flex-shrink-0 flex gap-2">
						<!-- EU Flag -->
						<svg class="h-8 w-12" viewBox="0 0 810 540">
							<rect fill="#039" width="810" height="540"/>
							<g fill="#fc0">
								<g id="s">
									<g id="c"><path d="M405,60l9.57,29.44H446.5l-25.87,18.79,9.88,30.41L405,120l-25.51,18.64,9.88-30.41-25.87-18.79h31.93z"/></g>
									<use href="#c" transform="rotate(30,405,270)"/>
									<use href="#c" transform="rotate(60,405,270)"/>
									<use href="#c" transform="rotate(90,405,270)"/>
									<use href="#c" transform="rotate(120,405,270)"/>
									<use href="#c" transform="rotate(150,405,270)"/>
								</g>
								<use href="#s" transform="rotate(180,405,270)"/>
							</g>
						</svg>
						<!-- BMWK Logo placeholder -->
						<div class="h-8 w-8 bg-white/20 rounded flex items-center justify-center text-xs">BMWK</div>
					</div>
					<p class="text-gray-400 text-xs leading-relaxed">
						{$t('footer.fundingNotice')}
						<a href="/sonar" class="text-[#06E481] hover:underline ml-1">{$t('footer.fundingNoticeLink')}</a>
					</p>
				</div>
			</div>

			<!-- Bottom Bar -->
			<div class="mt-8 pt-8 border-t border-gray-600">
				<div class="flex flex-col md:flex-row justify-between items-center">
					<p class="text-gray-400 text-sm">
						© {new Date().getFullYear()} startneu. {$t('footer.rights')}
					</p>
					<p class="text-gray-400 text-sm mt-2 md:mt-0">
						{$t('footer.madeWith')} <span class="text-[#06E481]">♥</span> {$t('footer.location')}
					</p>
				</div>
			</div>
		</div>
	</footer>

	<!-- Admin Button (fixed bottom right) -->
	{#if $auth.isAdmin}
		<a
			href="/admin"
			class="fixed bottom-6 right-6 p-3 bg-gray-800 dark:bg-gray-700 text-white rounded-full shadow-lg hover:bg-gray-700 dark:hover:bg-gray-600 transition-colors z-50"
			title={$t('nav.admin')}
		>
			<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
			</svg>
		</a>
	{/if}
</div>
