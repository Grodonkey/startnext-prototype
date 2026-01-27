<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/language';
	import { listFeaturedProjects } from '$lib/api';
	import { getProjectTypeButtonClass, getImageUrl, getAvatarUrl } from '$lib/utils';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import Alert from '$lib/components/Alert.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Badge from '$lib/components/Badge.svelte';
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import Avatar from '$lib/components/Avatar.svelte';

	let projects = [];
	let loading = true;
	let error = null;
	let currentIndex = 0;
	let feedContainer;

	onMount(async () => {
		try {
			// Get more projects for the feed
			projects = await listFeaturedProjects(20);
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	function handleScroll() {
		if (!feedContainer) return;
		const scrollTop = feedContainer.scrollTop;
		const itemHeight = feedContainer.clientHeight;
		currentIndex = Math.round(scrollTop / itemHeight);
	}

	function scrollToProject(index) {
		if (!feedContainer) return;
		const itemHeight = feedContainer.clientHeight;
		feedContainer.scrollTo({
			top: index * itemHeight,
			behavior: 'smooth'
		});
	}

	function nextProject() {
		if (currentIndex < projects.length - 1) {
			scrollToProject(currentIndex + 1);
		}
	}

	function previousProject() {
		if (currentIndex > 0) {
			scrollToProject(currentIndex - 1);
		}
	}

	function handleKeydown(event) {
		if (event.key === 'ArrowDown' || event.key === 'j') {
			event.preventDefault();
			nextProject();
		} else if (event.key === 'ArrowUp' || event.key === 'k') {
			event.preventDefault();
			previousProject();
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="h-[calc(100vh-4rem)] bg-black overflow-hidden">
	{#if loading}
		<div class="h-full flex items-center justify-center">
			<LoadingSpinner size="lg" />
		</div>
	{:else if error}
		<div class="h-full flex items-center justify-center px-4">
			<Alert type="error" message={error} />
		</div>
	{:else if projects.length === 0}
		<div class="h-full flex items-center justify-center px-4">
			<EmptyState message={$t('discover.noFeatured')} />
		</div>
	{:else}
		<!-- Feed Container -->
		<div
			bind:this={feedContainer}
			on:scroll={handleScroll}
			class="h-full overflow-y-scroll snap-y snap-mandatory scrollbar-hide"
		>
			{#each projects as project, index}
				<div class="h-full snap-start snap-always flex items-center justify-center p-4">
					<!-- Project Card (9:16 aspect ratio) -->
					<div class="relative w-full max-w-[400px] aspect-[9/16] bg-gray-900 rounded-2xl overflow-hidden shadow-2xl">
						<!-- Background Image -->
						{#if project.image_url}
							<img
								src={getImageUrl(project.image_url)}
								alt={project.title}
								class="absolute inset-0 w-full h-full object-cover"
							/>
							<div class="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent"></div>
						{:else}
							<div class="absolute inset-0 bg-gradient-to-br from-[#304b50] to-[#06E481]"></div>
							<div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
						{/if}

						<!-- Project Type Badge -->
						<div class="absolute top-4 left-4">
							<Badge type="projectType" value={project.project_type || 'crowdfunding'} variant="light" />
						</div>

						<!-- Content Overlay -->
						<div class="absolute inset-0 flex flex-col justify-end p-6">
							<!-- Project Info -->
							<div class="mb-4">
								<a href="/projects/{project.slug}" class="block">
									<h2 class="text-2xl font-bold text-white mb-2 hover:text-[#06E481] transition-colors">
										{project.title}
									</h2>
								</a>
								{#if project.short_description}
									<p class="text-gray-200 text-sm line-clamp-3 mb-4">
										{project.short_description}
									</p>
								{/if}

								<!-- Owner -->
								{#if project.owner}
									<a
										href="/profile/{project.owner.profile_slug}"
										class="inline-flex items-center text-gray-300 hover:text-[#06E481] transition-colors text-sm mb-4"
									>
										<div class="mr-2">
											<Avatar name={project.owner.full_name} imageUrl={getAvatarUrl(project.owner.avatar_url)} size="sm" />
										</div>
										{project.owner.full_name || project.owner.email}
									</a>
								{/if}
							</div>

							<!-- Funding Progress -->
							{#if project.funding_goal}
								<div class="mb-4">
									<ProgressBar
										current={project.funding_current}
										goal={project.funding_goal}
										projectType={project.project_type}
									/>
								</div>
							{/if}

							<!-- Support Button -->
							{#if project.status === 'financing'}
								<button
									class="w-full py-4 px-6 font-bold text-lg rounded-xl transition-colors {getProjectTypeButtonClass(project.project_type)}"
								>
									{$t('project.support')}
								</button>
							{:else}
								<a
									href="/projects/{project.slug}"
									class="block w-full py-4 px-6 font-bold text-lg rounded-xl transition-colors text-center {getProjectTypeButtonClass(project.project_type)}"
								>
									{$t('project.viewProject')}
								</a>
							{/if}
						</div>

						<!-- Progress Indicator -->
						<div class="absolute top-4 right-4 flex flex-col gap-1">
							{#each projects as _, i}
								<div
									class="w-1 h-4 rounded-full transition-all {i === currentIndex ? 'bg-[#06E481]' : 'bg-white/30'}"
								></div>
							{/each}
						</div>
					</div>
				</div>
			{/each}
		</div>

		<!-- Navigation Hints -->
		<div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-4 text-gray-500 text-sm">
			<span class="hidden sm:inline">{$t('discover.scrollHint')}</span>
		</div>

		<!-- Navigation Buttons (Desktop) -->
		<div class="hidden sm:flex absolute right-4 top-1/2 -translate-y-1/2 flex-col gap-2">
			<button
				on:click={previousProject}
				disabled={currentIndex === 0}
				class="p-3 rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
			>
				<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
				</svg>
			</button>
			<button
				on:click={nextProject}
				disabled={currentIndex === projects.length - 1}
				class="p-3 rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
			>
				<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
		</div>
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
	.line-clamp-3 {
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
