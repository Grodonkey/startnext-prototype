<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/language';
	import { listFeaturedProjects, listNearGoalProjects, getSuccessfulStarters } from '$lib/api';
	import { formatCurrency, calculateProgress, getImageUrl, getAvatarUrl } from '$lib/utils';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import Alert from '$lib/components/Alert.svelte';
	import Badge from '$lib/components/Badge.svelte';
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import Avatar from '$lib/components/Avatar.svelte';

	let featuredProjects = [];
	let nearGoalProjects = [];
	let successfulStarters = [];
	let loading = true;
	let error = null;

	// Slider state
	let sliderContainer;
	let canScrollLeft = false;
	let canScrollRight = true;

	onMount(async () => {
		try {
			const [featured, nearGoal, starters] = await Promise.all([
				listFeaturedProjects(4),
				listNearGoalProjects(80, 10),
				getSuccessfulStarters(4)
			]);
			featuredProjects = featured;
			nearGoalProjects = nearGoal;
			successfulStarters = starters;
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	function scrollSlider(direction) {
		if (!sliderContainer) return;
		const scrollAmount = 320;
		sliderContainer.scrollBy({
			left: direction === 'left' ? -scrollAmount : scrollAmount,
			behavior: 'smooth'
		});
	}

	function updateScrollButtons() {
		if (!sliderContainer) return;
		canScrollLeft = sliderContainer.scrollLeft > 0;
		canScrollRight = sliderContainer.scrollLeft < sliderContainer.scrollWidth - sliderContainer.clientWidth - 10;
	}
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	{#if loading}
		<div class="text-center py-12">
			<LoadingSpinner />
		</div>
	{:else if error}
		<Alert type="error" message={error} />
	{:else}
		<!-- Featured Projects Section -->
		<section class="mb-16">
			<h2 class="text-2xl font-semibold text-[#304b50] dark:text-white mb-6">
				{$t('discover.featured')}
			</h2>

			{#if featuredProjects.length > 0}
				<div class="flex flex-col lg:flex-row gap-6">
					<!-- Main Featured Project (60%) -->
					<div class="lg:w-3/5">
						<a href="/projects/{featuredProjects[0].slug}" class="block group">
							<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden h-full">
								<div class="relative aspect-[16/9]">
									{#if featuredProjects[0].image_url}
										<img
											src={getImageUrl(featuredProjects[0].image_url)}
											alt={featuredProjects[0].title}
											class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
										/>
									{:else}
										<div class="w-full h-full bg-gradient-to-br from-[#304b50] to-[#06E481] flex items-center justify-center">
											<svg class="h-24 w-24 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
											</svg>
										</div>
									{/if}
									<div class="absolute top-4 left-4 flex gap-2">
										<Badge type="projectType" value={featuredProjects[0].project_type || 'crowdfunding'} />
									</div>
								</div>
								<div class="p-6">
									<h3 class="text-xl font-bold text-[#304b50] dark:text-white mb-2 group-hover:text-[#06E481] transition-colors">
										{featuredProjects[0].title}
									</h3>
									{#if featuredProjects[0].short_description}
										<p class="text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
											{featuredProjects[0].short_description}
										</p>
									{/if}
									{#if featuredProjects[0].funding_goal}
										<div class="mt-4">
											<ProgressBar
												current={featuredProjects[0].funding_current}
												goal={featuredProjects[0].funding_goal}
												projectType={featuredProjects[0].project_type}
												showGoal={false}
											/>
										</div>
									{/if}
									{#if featuredProjects[0].status === 'financing'}
										<button
											on:click|preventDefault|stopPropagation={() => {}}
											class="mt-4 w-full py-2 px-4 bg-[#06E481] text-[#304b50] font-semibold rounded-lg hover:bg-[#05b667] transition-colors"
										>
											{$t('project.support')}
										</button>
									{/if}
								</div>
							</div>
						</a>
					</div>

					<!-- Side Featured Projects (40%) -->
					<div class="lg:w-2/5 flex flex-col gap-4">
						{#each featuredProjects.slice(1, 4) as project}
							<a href="/projects/{project.slug}" class="block group">
								<div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden flex h-32">
									<div class="w-1/3 flex-shrink-0">
										{#if project.image_url}
											<img
												src={getImageUrl(project.image_url)}
												alt={project.title}
												class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
											/>
										{:else}
											<div class="w-full h-full bg-gradient-to-br from-[#304b50] to-[#06E481] flex items-center justify-center">
												<svg class="h-8 w-8 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
												</svg>
											</div>
										{/if}
									</div>
									<div class="flex-1 p-4 flex flex-col justify-between">
										<h3 class="font-semibold text-[#304b50] dark:text-white group-hover:text-[#06E481] transition-colors line-clamp-2">
											{project.title}
										</h3>
										{#if project.funding_goal}
											<div>
												<div class="flex justify-between text-xs mb-1">
													<span class="text-[#304b50] dark:text-white font-medium">
														{calculateProgress(project.funding_current, project.funding_goal)}%
													</span>
												</div>
												<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
													<div
														class="bg-[#06E481] h-1.5 rounded-full"
														style="width: {calculateProgress(project.funding_current, project.funding_goal)}%"
													></div>
												</div>
											</div>
										{/if}
									</div>
								</div>
							</a>
						{/each}
					</div>
				</div>
			{:else}
				<!-- Placeholder for Featured Projects -->
				<div class="flex flex-col lg:flex-row gap-6">
					<!-- Main Placeholder (60%) -->
					<div class="lg:w-3/5">
						<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden h-full">
							<div class="relative aspect-[16/9] bg-gray-200 dark:bg-gray-700 animate-pulse">
								<div class="absolute inset-0 flex items-center justify-center">
									<svg class="h-24 w-24 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
									</svg>
								</div>
								<div class="absolute top-4 left-4">
									<span class="bg-gray-300 dark:bg-gray-600 text-transparent px-3 py-1 rounded-full text-sm">
										{$t('discover.featuredBadge')}
									</span>
								</div>
							</div>
							<div class="p-6">
								<div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-3 animate-pulse"></div>
								<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2 animate-pulse"></div>
								<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3 mb-4 animate-pulse"></div>
								<div class="mt-4">
									<div class="flex justify-between mb-1">
										<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 animate-pulse"></div>
										<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-10 animate-pulse"></div>
									</div>
									<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2"></div>
								</div>
							</div>
						</div>
					</div>

					<!-- Side Placeholders (40%) -->
					<div class="lg:w-2/5 flex flex-col gap-4">
						{#each [1, 2, 3] as _}
							<div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden flex h-32">
								<div class="w-1/3 flex-shrink-0 bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center">
									<svg class="h-8 w-8 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
									</svg>
								</div>
								<div class="flex-1 p-4 flex flex-col justify-between">
									<div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4 animate-pulse"></div>
									<div>
										<div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 mb-1 animate-pulse"></div>
										<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5"></div>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>
				<p class="text-center text-gray-500 dark:text-gray-400 mt-6">{$t('discover.noFeatured')}</p>
			{/if}
		</section>

		<!-- Near Goal Projects Slider -->
		<section class="mb-16">
			<div class="flex justify-between items-center mb-6">
				<h2 class="text-2xl font-semibold text-[#304b50] dark:text-white">
					{$t('discover.nearGoal')}
				</h2>
				{#if nearGoalProjects.length > 0}
					<div class="flex gap-2">
						<button
							on:click={() => scrollSlider('left')}
							disabled={!canScrollLeft}
							class="p-2 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
						>
							<svg class="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
							</svg>
						</button>
						<button
							on:click={() => scrollSlider('right')}
							disabled={!canScrollRight}
							class="p-2 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
						>
							<svg class="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
						</button>
					</div>
				{/if}
			</div>

			{#if nearGoalProjects.length > 0}
				<div
					bind:this={sliderContainer}
					on:scroll={updateScrollButtons}
					class="flex gap-6 overflow-x-auto scrollbar-hide pb-4 -mx-4 px-4"
					style="scroll-snap-type: x mandatory;"
				>
					{#each nearGoalProjects as project}
						<a
							href="/projects/{project.slug}"
							class="flex-shrink-0 w-72 group"
							style="scroll-snap-align: start;"
						>
							<div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
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
									<div class="absolute top-2 left-2">
										<Badge type="projectType" value={project.project_type || 'crowdfunding'} />
									</div>
									<div class="absolute top-2 right-2">
										<span class="bg-green-500 text-white font-semibold px-2 py-1 rounded text-xs">
											{calculateProgress(project.funding_current, project.funding_goal)}%
										</span>
									</div>
								</div>
								<div class="p-4">
									<h3 class="font-semibold text-[#304b50] dark:text-white group-hover:text-[#06E481] transition-colors line-clamp-2 mb-2">
										{project.title}
									</h3>
									<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
										<div
											class="bg-[#06E481] h-2 rounded-full"
											style="width: {calculateProgress(project.funding_current, project.funding_goal)}%"
										></div>
									</div>
									<div class="flex justify-between text-sm mb-3">
										<span class="text-[#304b50] dark:text-white font-medium">
											{formatCurrency(project.funding_current)}
										</span>
										<span class="text-gray-500 dark:text-gray-400">
											{$t('project.goal')}: {formatCurrency(project.funding_goal)}
										</span>
									</div>
									<button
										on:click|preventDefault|stopPropagation={() => {}}
										class="w-full py-2 px-4 bg-[#06E481] text-[#304b50] font-semibold rounded-lg hover:bg-[#05b667] transition-colors text-sm"
									>
										{$t('project.support')}
									</button>
								</div>
							</div>
						</a>
					{/each}
				</div>
			{:else}
				<!-- Placeholder for Near Goal Projects -->
				<div class="flex gap-6 overflow-x-auto scrollbar-hide pb-4 -mx-4 px-4">
					{#each [1, 2, 3, 4] as _}
						<div class="flex-shrink-0 w-72">
							<div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
								<div class="relative aspect-video bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center">
									<svg class="h-12 w-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
									</svg>
									<div class="absolute top-2 right-2">
										<span class="bg-gray-300 dark:bg-gray-600 text-transparent px-2 py-1 rounded text-xs">80%</span>
									</div>
								</div>
								<div class="p-4">
									<div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-3 animate-pulse"></div>
									<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2"></div>
									<div class="flex justify-between">
										<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16 animate-pulse"></div>
										<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 animate-pulse"></div>
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
				<p class="text-center text-gray-500 dark:text-gray-400 mt-4">{$t('discover.noNearGoal')}</p>
			{/if}
		</section>

		<!-- Successful Starters Section -->
		<section>
			<h2 class="text-2xl font-semibold text-[#304b50] dark:text-white mb-6">
				{$t('discover.successfulStarters')}
			</h2>

			{#if successfulStarters.length > 0}
				<div class="flex flex-wrap justify-center gap-8">
					{#each successfulStarters as starter}
						<a href="/profile/{starter.profile_slug}" class="group text-center">
							<div class="mb-3 mx-auto group-hover:scale-110 transition-transform shadow-lg">
								<Avatar name={starter.full_name} size="xl" />
							</div>
							<h3 class="font-semibold text-[#304b50] dark:text-white group-hover:text-[#06E481] transition-colors">
								{starter.full_name || $t('discover.anonymous')}
							</h3>
							<p class="text-sm text-gray-500 dark:text-gray-400">
								{starter.successful_projects_count} {starter.successful_projects_count === 1 ? $t('discover.project') : $t('discover.projects')}
							</p>
							<p class="text-sm text-[#06E481] font-medium">
								{formatCurrency(starter.total_funding_raised)}
							</p>
						</a>
					{/each}
				</div>
			{:else}
				<!-- Placeholder for Successful Starters -->
				<div class="flex flex-wrap justify-center gap-8">
					{#each [1, 2, 3, 4] as _}
						<div class="text-center">
							<div class="w-24 h-24 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center mb-3 mx-auto shadow-lg">
								<svg class="h-10 w-10 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
								</svg>
							</div>
							<div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-24 mx-auto mb-2 animate-pulse"></div>
							<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16 mx-auto mb-1 animate-pulse"></div>
							<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 mx-auto animate-pulse"></div>
						</div>
					{/each}
				</div>
				<p class="text-center text-gray-500 dark:text-gray-400 mt-6">{$t('discover.noStarters')}</p>
			{/if}
		</section>
	{/if}
</div>

<style>
	.scrollbar-hide {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
	.scrollbar-hide::-webkit-scrollbar {
		display: none;
	}
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
