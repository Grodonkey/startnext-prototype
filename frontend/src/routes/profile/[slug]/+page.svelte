<script>
	import { page } from '$app/stores';
	import { t } from '$lib/stores/language';
	import { getPublicProfile } from '$lib/api';
	import { formatCurrency, calculateProgress, formatDate, getStatusColor, getImageUrl, getAvatarUrl } from '$lib/utils';
	import Avatar from '$lib/components/Avatar.svelte';

	let profile = null;
	let loading = true;
	let error = null;

	$: profileSlug = $page.params.slug;

	// Track previous slug to detect changes
	let previousSlug = null;

	$: if (profileSlug && profileSlug !== previousSlug) {
		previousSlug = profileSlug;
		loadProfile();
	}

	async function loadProfile() {
		loading = true;
		error = null;
		try {
			profile = await getPublicProfile(profileSlug);
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="mb-8">
		<button
			on:click={() => history.back()}
			class="text-[#304b50] dark:text-[#06E481] hover:underline flex items-center"
		>
			<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			{$t('project.back')}
		</button>
	</div>

	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-[#06E481]"></div>
			<p class="mt-4 text-gray-600 dark:text-gray-400">{$t('common.loading')}</p>
		</div>
	{:else if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded">
			{error}
		</div>
	{:else if profile}
		<!-- Profile Header -->
		<div class="bg-white dark:bg-gray-800 shadow rounded-lg p-8 mb-8">
			<div class="flex flex-col sm:flex-row items-center sm:items-start gap-6">
				<!-- Avatar -->
				<div class="flex-shrink-0">
					<Avatar name={profile.full_name} imageUrl={getAvatarUrl(profile.avatar_url)} size="xl" />
				</div>

				<!-- Info -->
				<div class="text-center sm:text-left">
					<h1 class="text-2xl font-bold text-[#304b50] dark:text-white">
						{profile.full_name || $t('discover.anonymous')}
					</h1>
					<p class="text-gray-600 dark:text-gray-400 mt-1">
						{$t('publicProfile.memberSince')} {formatDate(profile.created_at)}
					</p>
          
          <div class="flex flex-wrap gap-2 mt-2">
						{#if profile.projects.length >= 3}
							<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#FFC21C]/20 text-[#FFC21C]">
								{$t('profile.serialStarter')}
							</span>
						{/if}
						{#if profile.is_starter}
							<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#06E481]/20 text-[#304b50] dark:text-[#06E481]">
								<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
								</svg>
								{$t('publicProfile.projectStarter')}
							</span>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Projects Section -->
		<div class="bg-white dark:bg-gray-800 shadow rounded-lg p-8">
			<h2 class="text-xl font-semibold text-[#304b50] dark:text-white mb-6">
				{$t('publicProfile.projects')} ({profile.projects.length})
			</h2>

			{#if profile.projects.length > 0}
				<div class="grid gap-6 md:grid-cols-2">
					{#each profile.projects as project}
						<a href="/projects/{project.slug}" class="group">
							<div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
								<div class="relative aspect-video">
									{#if project.image_url}
										<img
											src={getImageUrl(project.image_url)}
											alt={project.title}
											class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
										/>
									{:else}
										<div class="w-full h-full bg-gradient-to-br from-[#304b50] to-[#06E481] flex items-center justify-center">
											<svg class="h-12 w-12 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
											</svg>
										</div>
									{/if}
									<div class="absolute top-2 right-2">
										<span class="px-2 py-1 rounded text-xs font-medium {getStatusColor(project.status)}">
											{$t(`project.status.${project.status}`)}
										</span>
									</div>
								</div>
								<div class="p-4">
									<h3 class="font-semibold text-[#304b50] dark:text-white group-hover:text-[#06E481] transition-colors mb-2">
										{project.title}
									</h3>
									{#if project.short_description}
										<p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
											{project.short_description}
										</p>
									{/if}
									{#if project.funding_goal}
										<div>
											<div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 mb-1">
												<div
													class="bg-[#06E481] h-2 rounded-full"
													style="width: {calculateProgress(project.funding_current, project.funding_goal)}%"
												></div>
											</div>
											<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
												<span>{formatCurrency(project.funding_current)}</span>
												<span>{calculateProgress(project.funding_current, project.funding_goal)}%</span>
											</div>
										</div>
									{/if}
								</div>
							</div>
						</a>
					{/each}
				</div>
			{:else}
				<p class="text-gray-500 dark:text-gray-400 text-center py-8">
					{$t('publicProfile.noProjects')}
				</p>
			{/if}
		</div>
	{/if}
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
