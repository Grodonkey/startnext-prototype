<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/language';
	import { getAllStarters } from '$lib/api';
	import { formatCurrency, formatProjectCount, getAvatarUrl } from '$lib/utils';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import Alert from '$lib/components/Alert.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Avatar from '$lib/components/Avatar.svelte';

	let starters = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			starters = await getAllStarters(0, 100);
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="text-center mb-12">
		<h1 class="text-3xl font-bold text-[#304b50] dark:text-white mb-4">
			{$t('community.title')}
		</h1>
		<p class="text-gray-600 dark:text-gray-400 text-lg">
			{$t('community.subtitle')}
		</p>
	</div>

	{#if loading}
		<div class="text-center py-12">
			<LoadingSpinner />
		</div>
	{:else if error}
		<Alert type="error" message={error} />
	{:else if starters.length === 0}
		<EmptyState icon="users" message={$t('community.noStarters')} />
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
			{#each starters as starter}
				<a href="/profile/{starter.profile_slug}" class="group">
					<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
						<div class="flex items-center mb-4">
							<div class="flex-shrink-0 group-hover:scale-110 transition-transform">
								<Avatar name={starter.full_name} imageUrl={getAvatarUrl(starter.avatar_url)} size="lg" />
							</div>
							<div class="ml-4">
								<h3 class="font-semibold text-[#304b50] dark:text-white group-hover:text-[#06E481] transition-colors">
									{starter.full_name}
								</h3>
								<div class="flex flex-wrap gap-1 mt-1">
									{#if starter.project_count >= 3}
										<span class="inline-block px-2 py-0.5 bg-[#FFC21C]/20 text-[#FFC21C] text-xs font-medium rounded-full">
											{$t('profile.serialStarter')}
										</span>
									{/if}
									<span class="inline-block px-2 py-0.5 bg-[#06E481]/20 text-[#304b50] dark:text-[#06E481] text-xs font-medium rounded-full">
										{$t('profile.starter')}
									</span>
								</div>
							</div>
						</div>
						<div class="border-t border-gray-200 dark:border-gray-700 pt-4">
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">
									{formatProjectCount(starter.project_count, $t)}
								</span>
								{#if starter.total_funding_raised > 0}
									<span class="text-[#06E481] font-medium">
										{formatCurrency(starter.total_funding_raised)}
									</span>
								{/if}
							</div>
						</div>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>
