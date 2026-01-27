<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getCurrentUser, updateProfile, setup2FA, verify2FA, disable2FA, isAuthenticated, listMyProjects, logout, uploadAvatar, deleteAvatar } from '$lib/api';
	import { t } from '$lib/stores/language';
	import { auth } from '$lib/stores/auth';
	import { getAvatarUrl } from '$lib/utils';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import Alert from '$lib/components/Alert.svelte';
	import Badge from '$lib/components/Badge.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Avatar from '$lib/components/Avatar.svelte';

	let user = null;
	let loading = true;
	let error = '';
	let success = '';

	let fullName = '';
	let newPassword = '';
	let confirmPassword = '';

	let twoFactorSecret = '';
	let twoFactorQRCode = '';
	let twoFactorVerifyCode = '';
	let show2FASetup = false;

	let projects = [];
	let projectsLoading = true;

	// Avatar upload state
	let avatarUploading = false;
	let avatarInput;

	// Tab state: 'overview' or 'settings'
	let activeTab = 'overview';

	async function handleAvatarUpload(event) {
		const file = event.target.files?.[0];
		if (!file) return;

		// Validate file type
		if (!file.type.startsWith('image/')) {
			error = 'Please select an image file';
			return;
		}

		// Validate file size (max 5MB)
		if (file.size > 5 * 1024 * 1024) {
			error = 'Image must be smaller than 5MB';
			return;
		}

		avatarUploading = true;
		error = '';

		try {
			const result = await uploadAvatar(file);
			user.avatar_url = result.avatar_url;
			success = $t('profile.saved');
		} catch (err) {
			error = err.message;
		} finally {
			avatarUploading = false;
			// Reset input so same file can be selected again
			if (avatarInput) avatarInput.value = '';
		}
	}

	async function handleDeleteAvatar() {
		if (!user.avatar_url) return;

		avatarUploading = true;
		error = '';

		try {
			await deleteAvatar();
			user.avatar_url = null;
			success = $t('profile.saved');
		} catch (err) {
			error = err.message;
		} finally {
			avatarUploading = false;
		}
	}

	onMount(async () => {
		if (!isAuthenticated()) {
			goto('/login');
			return;
		}

		try {
			user = await getCurrentUser();
			fullName = user.full_name || '';
		} catch (err) {
			error = err.message;
			goto('/login');
		} finally {
			loading = false;
		}

		// Load user's projects
		try {
			projects = await listMyProjects();
		} catch (err) {
			console.log('Could not load projects:', err.message);
		} finally {
			projectsLoading = false;
		}
	});

	async function handleLogout() {
		try {
			await logout();
			goto('/');
		} catch (err) {
			console.error('Logout failed:', err);
			goto('/');
		}
	}

	async function handleUpdateProfile() {
		error = '';
		success = '';

		if (newPassword && newPassword !== confirmPassword) {
			error = $t('register.passwordMismatch');
			return;
		}

		try {
			const updateData = { full_name: fullName };
			if (newPassword) {
				updateData.password = newPassword;
			}

			user = await updateProfile(updateData);
			success = $t('profile.saved');
			newPassword = '';
			confirmPassword = '';
		} catch (err) {
			error = err.message;
		}
	}

	async function handleSetup2FA() {
		error = '';
		try {
			const response = await setup2FA();
			twoFactorSecret = response.secret;
			twoFactorQRCode = response.qr_code_url;
			show2FASetup = true;
		} catch (err) {
			error = err.message;
		}
	}

	async function handleVerify2FA() {
		error = '';
		success = '';
		try {
			await verify2FA(twoFactorVerifyCode);
			success = $t('profile.2faActivated');
			show2FASetup = false;
			user.two_factor_enabled = true;
			twoFactorVerifyCode = '';
		} catch (err) {
			error = err.message;
		}
	}

	async function handleDisable2FA() {
		error = '';
		success = '';
		try {
			await disable2FA(twoFactorVerifyCode);
			success = $t('profile.2faDeactivated');
			user.two_factor_enabled = false;
			twoFactorVerifyCode = '';
		} catch (err) {
			error = err.message;
		}
	}
</script>

{#if loading}
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
		<LoadingSpinner />
	</div>
{:else if user}
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
		<h1 class="text-3xl font-bold text-[#304b50] dark:text-white mb-6">{$t('profile.title')}</h1>

		<!-- Tab Navigation -->
		<div class="border-b border-gray-200 dark:border-gray-700 mb-6">
			<nav class="flex space-x-8">
				<button
					on:click={() => activeTab = 'overview'}
					class="py-3 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'overview'
						? 'border-[#304b50] text-[#304b50] dark:border-[#06E481] dark:text-[#06E481]'
						: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'}"
				>
					{$t('profile.overview')}
				</button>
				<button
					on:click={() => activeTab = 'settings'}
					class="py-3 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'settings'
						? 'border-[#304b50] text-[#304b50] dark:border-[#06E481] dark:text-[#06E481]'
						: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'}"
				>
					{$t('profile.settings')}
				</button>
			</nav>
		</div>

		<Alert type="error" message={error} />
		<Alert type="success" message={success} />

		<!-- Overview Tab -->
		{#if activeTab === 'overview'}
			<!-- Account Info -->
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
				<div class="flex justify-between items-start">
					<div class="flex-1">
						<h2 class="text-xl font-semibold text-[#304b50] dark:text-white mb-4">{$t('profile.accountInfo')}</h2>
						<div class="space-y-3">
							<div>
								<span class="font-medium text-gray-700 dark:text-gray-300">{$t('profile.fullName')}:</span>
								<span class="text-gray-600 dark:text-gray-400 ml-2">{user.full_name || '-'}</span>
							</div>
							<div>
								<span class="font-medium text-gray-700 dark:text-gray-300">{$t('profile.email')}:</span>
								<span class="text-gray-600 dark:text-gray-400 ml-2">{user.email}</span>
							</div>
							<div>
								<span class="font-medium text-gray-700 dark:text-gray-300">{$t('profile.status')}:</span>
								{#if user.is_active}
									<span class="ml-2 inline-block bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-400 px-2 py-1 rounded text-sm"
										>{$t('profile.active')}</span
									>
								{:else}
									<span class="ml-2 inline-block bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-400 px-2 py-1 rounded text-sm"
										>{$t('profile.inactive')}</span
									>
								{/if}
							</div>
							<div>
								<span class="font-medium text-gray-700 dark:text-gray-300">{$t('profile.role')}:</span>
								{#if user.is_admin}
									<span class="ml-2 inline-block bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 px-2 py-1 rounded text-sm"
										>{$t('profile.admin')}</span
									>
								{/if}
								{#if user.is_starter || projects.length > 0}
									<span class="ml-2 inline-block bg-[#06E481]/20 dark:bg-[#06E481]/20 text-[#304b50] dark:text-[#06E481] px-2 py-1 rounded text-sm"
										>{$t('profile.starter')}</span
									>
								{:else if !user.is_admin}
									<span class="ml-2 inline-block bg-gray-100 dark:bg-gray-700 text-[#304b50] dark:text-gray-300 px-2 py-1 rounded text-sm"
										>{$t('profile.supporter')}</span
									>
								{/if}
							</div>
						</div>
					</div>
					<!-- Avatar on the right -->
					<div class="flex-shrink-0 ml-6">
						<Avatar
							name={user.full_name || ''}
							imageUrl={getAvatarUrl(user.avatar_url)}
							size="xl"
						/>
					</div>
				</div>

				<!-- Logout Button -->
				<div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
					<button
						on:click={handleLogout}
						class="inline-flex items-center px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
					>
						<svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
						</svg>
						{$t('nav.logout')}
					</button>
				</div>
			</div>

			<!-- My Projects Section -->
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
				<div class="flex justify-between items-center mb-4">
					<h2 class="text-xl font-semibold text-[#304b50] dark:text-white">{$t('project.myProjects')}</h2>
					<a
						href="/projects/new"
						class="inline-flex items-center px-3 py-1 bg-[#06E481] text-[#304b50] font-semibold text-sm font-medium rounded-md hover:bg-[#05b667] transition-colors"
					>
						<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						{$t('project.create')}
					</a>
				</div>

				{#if projectsLoading}
					<LoadingSpinner size="sm" />
				{:else if projects.length === 0}
					<EmptyState message={$t('project.noProjects')}>
						<p class="text-sm text-gray-500 dark:text-gray-500">{$t('project.startFirst')}</p>
					</EmptyState>
				{:else}
					<div class="space-y-3">
						{#each projects as project}
							<a
								href="/projects/{project.slug}"
								class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
							>
								<div class="flex justify-between items-start">
									<div>
										<h3 class="font-medium text-[#304b50] dark:text-white">{project.title}</h3>
										{#if project.short_description}
											<p class="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-1">{project.short_description}</p>
										{/if}
									</div>
									<Badge type="status" value={project.status} />
								</div>
							</a>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Settings Tab -->
		{#if activeTab === 'settings'}
			<!-- Avatar Upload -->
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
				<h2 class="text-xl font-semibold text-[#304b50] dark:text-white mb-4">{$t('profile.avatar')}</h2>

				<div class="flex items-center gap-6">
					<Avatar
						name={user.full_name || ''}
						imageUrl={getAvatarUrl(user.avatar_url)}
						size="xl"
					/>

					<div class="flex flex-col gap-3">
						<input
							type="file"
							accept="image/*"
							bind:this={avatarInput}
							on:change={handleAvatarUpload}
							class="hidden"
							id="avatar-input"
						/>
						<button
							on:click={() => avatarInput?.click()}
							disabled={avatarUploading}
							class="px-4 py-2 bg-[#06E481] text-[#304b50] font-semibold rounded-md hover:bg-[#05b667] transition-colors disabled:opacity-50 flex items-center gap-2"
						>
							{#if avatarUploading}
								<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
							{:else}
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
							{/if}
							{$t('profile.uploadAvatar')}
						</button>

						{#if user.avatar_url}
							<button
								on:click={handleDeleteAvatar}
								disabled={avatarUploading}
								class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors disabled:opacity-50"
							>
								{$t('profile.deleteAvatar')}
							</button>
						{/if}
					</div>
				</div>
				<p class="mt-3 text-sm text-gray-500 dark:text-gray-400">{$t('profile.avatarHint')}</p>
			</div>

			<!-- Edit Profile -->
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
				<h2 class="text-xl font-semibold text-[#304b50] dark:text-white mb-4">{$t('profile.editProfile')}</h2>

				<form on:submit|preventDefault={handleUpdateProfile}>
					<div class="mb-4">
						<label for="fullName" class="block text-gray-700 dark:text-gray-300 font-medium mb-2">{$t('profile.fullName')}</label>
						<input
							type="text"
							id="fullName"
							bind:value={fullName}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-[#06E481] bg-white dark:bg-gray-700 text-[#304b50] dark:text-white"
						/>
					</div>

					<div class="mb-4">
						<label for="newPassword" class="block text-gray-700 dark:text-gray-300 font-medium mb-2"
							>{$t('profile.newPassword')}</label
						>
						<input
							type="password"
							id="newPassword"
							bind:value={newPassword}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-[#06E481] bg-white dark:bg-gray-700 text-[#304b50] dark:text-white"
						/>
					</div>

					{#if newPassword}
						<div class="mb-6">
							<label for="confirmPassword" class="block text-gray-700 dark:text-gray-300 font-medium mb-2"
								>{$t('register.confirmPassword')}</label
							>
							<input
								type="password"
								id="confirmPassword"
								bind:value={confirmPassword}
								class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-[#06E481] bg-white dark:bg-gray-700 text-[#304b50] dark:text-white"
							/>
						</div>
					{/if}

					<button
						type="submit"
						class="bg-[#06E481] text-[#304b50] font-semibold py-2 px-4 rounded-md hover:bg-[#05b667] transition-colors"
					>
						{$t('profile.updateProfile')}
					</button>
				</form>
			</div>

			<!-- 2FA Section -->
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
				<h2 class="text-xl font-semibold text-[#304b50] dark:text-white mb-4">{$t('profile.2fa')}</h2>

				{#if user.two_factor_enabled}
					<div class="mb-4">
						<p class="text-green-600 dark:text-green-400 mb-4">{$t('profile.2faEnabled')}</p>
						<div class="mb-4">
							<label for="disableCode" class="block text-gray-700 dark:text-gray-300 font-medium mb-2"
								>{$t('profile.enterDisableCode')}</label
							>
							<input
								type="text"
								id="disableCode"
								bind:value={twoFactorVerifyCode}
								placeholder="123456"
								class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-[#06E481] bg-white dark:bg-gray-700 text-[#304b50] dark:text-white"
							/>
						</div>
						<button
							on:click={handleDisable2FA}
							class="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors"
						>
							{$t('profile.disable2fa')}
						</button>
					</div>
				{:else}
					{#if !show2FASetup}
						<p class="text-gray-600 dark:text-gray-400 mb-4">{$t('profile.2faDisabled')}</p>
						<button
							on:click={handleSetup2FA}
							class="bg-[#06E481] text-[#304b50] font-semibold py-2 px-4 rounded-md hover:bg-[#05b667] transition-colors"
						>
							{$t('profile.2faSetup')}
						</button>
					{:else}
						<div class="space-y-4">
							<p class="text-gray-700 dark:text-gray-300">{$t('profile.scanQRCode')}</p>
							{#if twoFactorQRCode}
								<img src={twoFactorQRCode} alt="QR Code" class="mx-auto" />
							{/if}
							<p class="text-sm text-gray-600 dark:text-gray-400">{$t('profile.manualCode')}</p>
							<p class="font-mono text-sm bg-gray-100 dark:bg-gray-700 text-[#304b50] dark:text-gray-200 p-2 rounded">{twoFactorSecret}</p>

							<div class="mb-4">
								<label for="verifyCode" class="block text-gray-700 dark:text-gray-300 font-medium mb-2"
									>{$t('profile.enterVerifyCode')}</label
								>
								<input
									type="text"
									id="verifyCode"
									bind:value={twoFactorVerifyCode}
									placeholder="123456"
									class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-[#06E481] bg-white dark:bg-gray-700 text-[#304b50] dark:text-white"
								/>
							</div>

							<button
								on:click={handleVerify2FA}
								class="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
							>
								{$t('profile.enable2fa')}
							</button>
							<button
								on:click={() => (show2FASetup = false)}
								class="ml-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 py-2 px-4 rounded-md hover:bg-gray-400 dark:hover:bg-gray-500 transition-colors"
							>
								{$t('common.cancel')}
							</button>
						</div>
					{/if}
				{/if}
			</div>
		{/if}
	</div>
{/if}
