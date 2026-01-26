<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/stores/language';
	import { auth } from '$lib/stores/auth';
	import { suggestSlug, createProject, isAuthenticated } from '$lib/api';
	import { pricing, products, selectedProduct, getDiscountTier } from '$lib/stores/pricing';
	import { getPricingContent } from '$lib/data/pricingContent';
	import AuthForm from '$lib/components/AuthForm.svelte';
	import PlanTypeCard from '$lib/components/pricing/PlanTypeCard.svelte';
	import PlanCard from '$lib/components/pricing/PlanCard.svelte';
	import FundingSlider from '$lib/components/pricing/FundingSlider.svelte';
	import VoucherInput from '$lib/components/pricing/VoucherInput.svelte';
	import FundingTargetInput from '$lib/components/pricing/FundingTargetInput.svelte';
	import StartDateInput from '$lib/components/pricing/StartDateInput.svelte';
	import '$lib/styles/cf-plan-selection.scss';
	import '$lib/styles/cf-type-selection.scss';

	const STORAGE_KEY = 'pendingProject';

	// Step management: 'selection' or 'form'
	let step = 'selection';

	// Form data
	let title = '';
	let slug = '';
	let slugEdited = false;
	let shortDescription = '';
	let description = '';
	let imageUrl = '';
	let videoUrl = '';
	let startDate = '';

	// Get pricing content for display
	let lang = 'de';
	$: content = getPricingContent(lang);

	// Reactive values from store
	$: selectedType = $pricing.selectedType;
	$: selectedPlan = $pricing.selectedPlan;
	$: fundingGoal = $pricing.fundingGoal;
	$: voucher = $pricing.voucher;
	$: productList = $products;
	$: selected = $selectedProduct;

	// Calculate effective provision with volume discount
	$: currentProvision = selected?.discountedProvision || selected?.provision || 0;
	$: tier = getDiscountTier(fundingGoal);
	$: effectiveProvision = currentProvision * (1 - tier.discount / 100);

	// Color mapping for types
	// crowdfunding = green (#06E481), fundraising = pink (#FF85FF), private = yellow (#FFC21C)
	const typeColors = {
		crowdfunding: {
			border: 'border-[#06E481]',
			bg: 'bg-[#06E481]',
			bgLight: 'bg-[#06E481]/10',
			text: 'text-[#06E481]',
			hover: 'hover:bg-[#05b667]'
		},
		fundraising: {
			border: 'border-[#FF85FF]',
			bg: 'bg-[#FF85FF]',
			bgLight: 'bg-[#FF85FF]/10',
			text: 'text-[#FF85FF]',
			hover: 'hover:bg-[#e070e0]'
		},
		private: {
			border: 'border-[#FFC21C]',
			bg: 'bg-[#FFC21C]',
			bgLight: 'bg-[#FFC21C]/10',
			text: 'text-[#FFC21C]',
			hover: 'hover:bg-[#e0aa00]'
		}
	};

	$: colors = typeColors[selectedType] || typeColors.crowdfunding;

	let loading = false;
	let error = null;
	let slugLoading = false;

	// Auth modal state
	let showAuthModal = false;
	let authMode = 'magic';

	// Check if mobile for compact view
	let isMobile = false;

	onMount(() => {
		checkMobile();
		window.addEventListener('resize', checkMobile);
		loadFormData();
		return () => window.removeEventListener('resize', checkMobile);
	});

	function checkMobile() {
		isMobile = window.innerWidth < 1024;
	}

	// Save form data to localStorage
	function saveFormData() {
		const data = {
			title,
			slug,
			slugEdited,
			shortDescription,
			description,
			imageUrl,
			videoUrl,
			startDate,
			selectedType,
			selectedPlan,
			fundingGoal,
			voucher
		};
		localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
	}

	// Load form data from localStorage
	function loadFormData() {
		const saved = localStorage.getItem(STORAGE_KEY);
		if (saved) {
			try {
				const data = JSON.parse(saved);
				title = data.title || '';
				slug = data.slug || '';
				slugEdited = data.slugEdited || false;
				shortDescription = data.shortDescription || '';
				description = data.description || '';
				imageUrl = data.imageUrl || '';
				videoUrl = data.videoUrl || '';
				startDate = data.startDate || '';
				if (data.selectedType) pricing.setType(data.selectedType);
				if (data.selectedPlan) pricing.setPlan(data.selectedPlan);
				if (data.fundingGoal) pricing.setFundingGoal(data.fundingGoal);
				if (data.voucher?.isValid) pricing.setVoucher(data.voucher);
				return true;
			} catch (e) {
				console.error('Failed to load saved form data:', e);
			}
		}
		return false;
	}

	// Clear saved form data
	function clearFormData() {
		localStorage.removeItem(STORAGE_KEY);
	}

	// Plan selection handlers
	function handleTypeSelect(event) {
		pricing.setType(event.detail.type);
	}

	function handlePlanSelect(event) {
		pricing.setPlan(event.detail.plan);
	}

	// Handle CTA button click in plan card - go directly to form
	function handlePlanContinue(event) {
		pricing.setPlan(event.detail.plan);
		step = 'form';
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	function handleFundingChange(event) {
		pricing.setFundingGoal(event.detail);
	}

	function handleStartDateChange(event) {
		startDate = event.detail;
	}

	function handleVoucherApply(event) {
		pricing.setVoucher(event.detail);
	}

	function handleVoucherReset() {
		pricing.resetVoucher();
	}

	function formatCurrency(amount) {
		return new Intl.NumberFormat('de-DE', {
			style: 'decimal',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}

	// Continue to form step (no auth required here)
	function handleContinueToForm() {
		step = 'form';
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	// Back to selection step
	function handleBackToSelection() {
		step = 'selection';
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	// Form handlers
	let debounceTimer;
	async function handleTitleChange() {
		if (slugEdited) return;

		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(async () => {
			if (title.trim()) {
				slugLoading = true;
				try {
					const result = await suggestSlug(title);
					if (!slugEdited) {
						slug = result.slug;
					}
				} catch (e) {
					console.error('Failed to suggest slug:', e);
				} finally {
					slugLoading = false;
				}
			}
		}, 300);
	}

	function handleSlugEdit() {
		slugEdited = true;
	}

	async function handleSubmit() {
		error = null;

		if (!title.trim()) {
			error = $t('project.titleRequired');
			return;
		}

		if (!slug.trim()) {
			error = $t('project.slugRequired');
			return;
		}

		// Check if user is authenticated
		if (!$auth.isAuthenticated) {
			saveFormData();
			showAuthModal = true;
			return;
		}

		await submitProject();
	}

	async function submitProject() {
		loading = true;
		error = null;

		try {
			const projectData = {
				title: title.trim(),
				slug: slug.trim(),
				short_description: shortDescription.trim() || null,
				description: description.trim() || null,
				funding_goal: fundingGoal || null,
				image_url: imageUrl.trim() || null,
				video_url: videoUrl.trim() || null,
				project_type: selectedType,
				plan: selectedPlan,
				provision: effectiveProvision || null,
				voucher_code: voucher.isValid ? voucher.code : null,
				start_date: startDate || null
			};

			const project = await createProject(projectData);
			clearFormData();
			pricing.reset();
			goto(`/projects/${project.slug}`);
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	function handleLoginSuccess() {
		showAuthModal = false;
		if (step === 'selection') {
			step = 'form';
		} else {
			submitProject();
		}
	}

	async function handleRegisterSuccess() {
		showAuthModal = false;
		if (step === 'selection') {
			step = 'form';
		} else {
			submitProject();
		}
	}

	function handleBeforeMagicLink() {
		saveFormData();
	}

	function handleModeChange(event) {
		authMode = event.detail.mode;
	}

	function closeAuthModal() {
		showAuthModal = false;
	}

	function handleLogin() {
		const returnUrl = encodeURIComponent('/projects/new');
		goto(`/login?redirect=${returnUrl}`);
	}
</script>

<svelte:head>
	<title>{step === 'selection' ? content.titles.selectType : $t('project.create')} | startneu</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	{#if step === 'selection'}
		<!-- STEP 1: Plan Selection -->
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">

			<!-- Step 1: Select Project Type -->
			<section class="mb-12">
				<h1 class="text-2xl md:text-3xl font-bold text-center text-[#304b50] dark:text-white mb-8">
					{content.titles.selectType}
				</h1>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 max-w-4xl mx-auto">
					{#each ['crowdfunding', 'fundraising', 'private'] as type}
						<PlanTypeCard
							{type}
							title={content.types[type].title}
							subtitle={content.types[type].subtitle}
							description={content.types[type].description}
							isSelected={selectedType === type}
							on:select={handleTypeSelect}
						/>
					{/each}
				</div>
			</section>

			<!-- Step 2: Select Funding Goal -->
			<section class="mb-12">
				<h2 class="text-2xl md:text-3xl font-bold text-center text-[#304b50] dark:text-white mb-8">
					{content.titles.selectFunding}
				</h2>

				<div class="max-w-2xl mx-auto">
					<FundingSlider
						value={fundingGoal}
						{selectedType}
						on:change={handleFundingChange}
					/>

					<!-- Funding calculation info -->
					{#if currentProvision > 0}
						<div class="mt-8 text-center text-gray-600 dark:text-gray-400">
							<p>
								Bei <strong>{effectiveProvision.toFixed(2).replace('.', ',')} %</strong> Provision
								erhältst du ca. <strong>{formatCurrency(Math.round(fundingGoal * (1 - effectiveProvision / 100 - 0.0415)))} €</strong>
								nach Abzug aller Gebühren.
							</p>
							{#if tier.discount > 0}
								<p class="mt-2 text-sm">
									Ab {formatCurrency(tier.threshold)} € erhältst du {tier.discount} % Mengenrabatt auf die Provision.
								</p>
							{/if}
						</div>
					{/if}
				</div>
			</section>

			<!-- Step 3: Select Plan -->
			<section class="mb-12">
				<h2 class="text-2xl md:text-3xl font-bold text-center text-[#304b50] dark:text-white mb-4">
					{content.titles.selectPlan}
				</h2>

				<div class="cf-plan-selection cf-plan-selection--gradient cf-plan-selection--{selectedType}" class:cf-plan-selection--compact={isMobile}>
					<!-- Voucher Input -->
					<VoucherInput
						{selectedType}
						{voucher}
						on:apply={handleVoucherApply}
						on:reset={handleVoucherReset}
					/>

					<!-- Plan Cards -->
					<div class="cf-plan-selection__items">
						{#each productList as plan (plan.key)}
							{@const planContent = content.plans[plan.key]}
							{@const isDisabled = !plan.isAvailable}
							{@const showDiscount = voucher.isValid && voucher.discount > 0 && (voucher.forPlans.length === 0 || voucher.forPlans.includes(plan.key))}
							<PlanCard
								{plan}
								content={planContent}
								{selectedType}
								isSelected={selectedPlan === plan.key}
								{isDisabled}
								{showDiscount}
								discountPercent={voucher.discount}
								variant={isMobile ? 'compact' : 'full'}
								on:select={handlePlanSelect}
								on:continue={handlePlanContinue}
							/>
						{/each}
					</div>

					<!-- Business offer note (disclaimer) -->
					{#if !isMobile}
						<div class="cf-plan-selection__disclaimer">
							<div class="flex">
								<svg class="w-6 h-6 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<div>
									<div class="font-semibold text-[#304b50] dark:text-white">{content.labels.businessOfferTitle || 'Unternehmen & Organisationen'}</div>
									<div class="text-gray-500 dark:text-gray-400 text-sm">{content.labels.businessOffer}</div>
								</div>
							</div>
						</div>
					{/if}
				</div>
			</section>
		</div>

	{:else}
		<!-- STEP 2: Project Form -->
		<div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<div class="mb-8">
				<button
					type="button"
					on:click={handleBackToSelection}
					class="text-[#304b50] dark:text-[#06E481] hover:underline flex items-center"
				>
					<svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
					{$t('pricing.changePlan')}
				</button>
			</div>

			<!-- Product Overview: Type Card + Plan Card -->
			{#if selected}
				<div class="product-info grid grid-cols-1 sm:grid-cols-2 gap-4">
					<!-- Type Card -->
					<div class="h-full">
						<PlanTypeCard
							type={selectedType}
							title={content.types[selectedType]?.title}
							subtitle={content.types[selectedType]?.subtitle}
							description={content.types[selectedType]?.description}
							isSelected={true}
						/>
					</div>

					<!-- Plan Card (Summary Variant) -->
					<div class="cf-plan-selection mt-3 sm:mt-0 h-full">
						<PlanCard
							plan={selected}
							content={content.plans[selectedPlan]}
							{selectedType}
							isSelected={false}
							isDisabled={false}
							showDiscount={voucher.isValid && voucher.discount > 0}
							discountPercent={voucher.discount}
							variant="summary"
						/>
					</div>
				</div>

				<!-- Funding Target Input -->
				<div class="flex flex-col md:flex-row items-center justify-between mt-8 md:mt-10 mb-2 md:mb-0">
					<div class="mt-3 mb-3 md:mb-1 md:mt-0 text-center md:text-left">
						<div class="text-xl font-semibold text-[#304b50] dark:text-white">
							Berechnetes Finanzierungsziel
						</div>
						<div class="text-sm text-gray-500 dark:text-gray-400">
							Du kannst das Ziel hier noch anpassen
						</div>
					</div>
					<FundingTargetInput
						value={fundingGoal}
						{selectedType}
						on:change={handleFundingChange}
					/>
				</div>

				<!-- Start Date Input -->
				<div class="flex flex-col md:flex-row items-center justify-between mb-3 mt-4 md:mb-0">
					<div class="mb-2 text-center md:text-left">
						<div class="text-xl font-semibold text-[#304b50] dark:text-white">
							Geplantes Startdatum
						</div>
						<div class="text-sm text-gray-500 dark:text-gray-400">
							Ab wann soll dein Projekt starten?
						</div>
					</div>
					<StartDateInput
						value={startDate}
						{selectedType}
						on:change={handleStartDateChange}
					/>
				</div>
			{/if}

			<div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mt-10">
				<h1 class="text-2xl font-bold text-[#304b50] dark:text-white mb-6">
					{$t('project.create')}
				</h1>

				{#if error}
					<div class="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded">
						{error}
					</div>
				{/if}

				<form on:submit|preventDefault={handleSubmit} class="space-y-6">
					<!-- Title -->
					<div>
						<label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$t('project.title')} *
						</label>
						<input
							type="text"
							id="title"
							bind:value={title}
							on:input={handleTitleChange}
							placeholder={$t('project.titlePlaceholder')}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-offset-0 dark:bg-gray-700 dark:text-white {colors.border} focus:{colors.border}"
							required
						/>
					</div>

					<!-- Slug -->
					<div>
						<label for="slug" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$t('project.slug')} *
						</label>
						<div class="relative">
							<input
								type="text"
								id="slug"
								bind:value={slug}
								on:input={handleSlugEdit}
								class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-offset-0 dark:bg-gray-700 dark:text-white {colors.border} focus:{colors.border}"
								required
							/>
							{#if slugLoading}
								<div class="absolute right-3 top-1/2 -translate-y-1/2">
									<div class="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 {colors.border} border-t-transparent"></div>
								</div>
							{/if}
						</div>
						<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
							{$t('project.slugHint')}
						</p>
					</div>

					<!-- Short Description -->
					<div>
						<label for="shortDescription" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$t('project.shortDescription')}
						</label>
						<textarea
							id="shortDescription"
							bind:value={shortDescription}
							rows="2"
							maxlength="500"
							placeholder={$t('project.shortDescriptionPlaceholder')}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-offset-0 dark:bg-gray-700 dark:text-white {colors.border} focus:{colors.border}"
						></textarea>
						<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
							{shortDescription.length}/500
						</p>
					</div>

					<!-- Description -->
					<div>
						<label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$t('project.description')}
						</label>
						<textarea
							id="description"
							bind:value={description}
							rows="6"
							placeholder={$t('project.descriptionPlaceholder')}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-offset-0 dark:bg-gray-700 dark:text-white {colors.border} focus:{colors.border}"
						></textarea>
					</div>

					<!-- Image URL -->
					<div>
						<label for="imageUrl" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$t('project.imageUrl')}
						</label>
						<input
							type="url"
							id="imageUrl"
							bind:value={imageUrl}
							placeholder="https://..."
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-offset-0 dark:bg-gray-700 dark:text-white {colors.border} focus:{colors.border}"
						/>
					</div>

					<!-- Video URL -->
					<div>
						<label for="videoUrl" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$t('project.videoUrl')}
						</label>
						<input
							type="url"
							id="videoUrl"
							bind:value={videoUrl}
							placeholder="https://..."
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-offset-0 dark:bg-gray-700 dark:text-white {colors.border} focus:{colors.border}"
						/>
					</div>

					<!-- Submit Button -->
					<div class="pt-4">
						<button
							type="submit"
							disabled={loading}
							class="w-full px-4 py-3 font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors
								{colors.bg} text-white {colors.hover}"
						>
							{loading ? $t('project.creating') : $t('project.create')}
						</button>
					</div>
				</form>
			</div>
		</div>
	{/if}
</div>

<!-- Auth Modal -->
{#if showAuthModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
		<div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
			<div class="flex justify-between items-center mb-6">
				<h3 class="text-xl font-bold text-[#304b50] dark:text-white">
					{$t('project.authRequired')}
				</h3>
				<button
					type="button"
					on:click={closeAuthModal}
					class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
				>
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
			<p class="text-gray-600 dark:text-gray-400 mb-6">
				{$t('project.authRequiredDesc')}
			</p>
			<AuthForm
				bind:mode={authMode}
				on:loginsuccess={handleLoginSuccess}
				on:registersuccess={handleRegisterSuccess}
				on:beforemagiclink={handleBeforeMagicLink}
				on:modechange={handleModeChange}
			/>
		</div>
	</div>
{/if}
