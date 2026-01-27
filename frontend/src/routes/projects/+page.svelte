<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/language';
	import { listProjects } from '$lib/api';
	import { formatCurrency, calculateProgress, getImageUrl } from '$lib/utils';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import Alert from '$lib/components/Alert.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import ProgressBar from '$lib/components/ProgressBar.svelte';

	let projects = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			projects = await listProjects(null, 0, 50);
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="flex justify-between items-center mb-8">
		<h1 class="text-3xl font-bold text-[#304b50] dark:text-white">
			{$t('home.featuredProjects')}
		</h1>
		<a
			href="/projects/new"
			class="inline-flex items-center px-4 py-2 bg-[#06E481] text-[#304b50] font-semibold font-medium rounded-md hover:bg-[#05b667] transition-colors"
		>
			<svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			{$t('home.cta')}
		</a>
	</div>

	{#if loading}
		<div class="text-center py-12">
			<LoadingSpinner />
		</div>
	{:else if error}
		<Alert type="error" message={error} />
	{:else if projects.length === 0}
		<EmptyState message={$t('home.noProjects')} />
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each projects as project}
				<a
					href="/projects/{project.slug}"
					class="block bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
				>
					{#if project.image_url}
						<img
							src={getImageUrl(project.image_url)}
							alt={project.title}
							class="w-full h-48 object-cover"
						/>
					{:else}
						<div class="w-full h-48 bg-gradient-to-br from-[#304b50] to-[#06E481] flex items-center justify-center">
							<svg class="h-16 w-16 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
							</svg>
						</div>
					{/if}
					<div class="p-4">
						<h3 class="text-lg font-semibold text-[#304b50] dark:text-white mb-2">
							{project.title}
						</h3>
						{#if project.short_description}
							<p class="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
								{project.short_description}
							</p>
						{/if}
						{#if project.funding_goal}
							<div class="mb-2">
								<ProgressBar
									current={project.funding_current}
									goal={project.funding_goal}
									projectType={project.project_type}
								/>
							</div>
						{/if}
					</div>
				</a>
			{/each}
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
