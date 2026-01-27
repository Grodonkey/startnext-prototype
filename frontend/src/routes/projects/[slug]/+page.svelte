<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t } from '$lib/stores/language';
	import { auth } from '$lib/stores/auth';
	import { getProject, updateProject, deleteProject, submitProject, duplicateProject, uploadProjectImage, deleteProjectImage } from '$lib/api';
	import { formatCurrency, calculateProgress, formatDate, getStatusColor, getProjectTypeColor, getImageUrl } from '$lib/utils';

	let project = null;
	let loading = true;
	let error = null;
	let success = null;
	let submitting = false;
	let deleting = false;
	let duplicating = false;
	let showDeleteConfirm = false;
	let showDuplicateConfirm = false;
	let showActionsMenu = false;
	let deleteConfirmSlug = '';

	// Edit mode state
	let editMode = false;
	let editingField = null;
	let saving = false;

	// Edit values for each field
	let editValues = {};

	// Image upload state
	let imageUploading = false;
	let imageInput;

	async function handleImageUpload(event) {
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

		imageUploading = true;
		error = null;

		try {
			const result = await uploadProjectImage(project.id, file);
			project.image_url = result.image_url;
			editingField = null;
			success = $t('project.updated');
			setTimeout(() => { success = null; }, 3000);
		} catch (err) {
			error = err.message;
		} finally {
			imageUploading = false;
			// Reset input so same file can be selected again
			if (imageInput) imageInput.value = '';
		}
	}

	async function handleDeleteImage() {
		if (!project.image_url) return;

		imageUploading = true;
		error = null;

		try {
			await deleteProjectImage(project.id);
			project.image_url = null;
			editingField = null;
			success = $t('project.updated');
			setTimeout(() => { success = null; }, 3000);
		} catch (err) {
			error = err.message;
		} finally {
			imageUploading = false;
		}
	}

	$: slug = $page.params.slug;
	$: isOwner = $auth.user && project && $auth.user.id === project.owner_id;
	$: isAdmin = $auth.isAdmin;
	$: canEdit = (isOwner && (project?.status === 'draft' || project?.status === 'submitted')) || isAdmin;

	// Track previous slug to detect changes
	let previousSlug = null;

	// Reactive: reload project when slug changes
	$: if (slug && slug !== previousSlug) {
		previousSlug = slug;
		loadProject();
	}

	async function loadProject() {
		loading = true;
		error = null;
		duplicating = false;
		editMode = false;
		editingField = null;
		try {
			project = await getProject(slug);
			initEditValues();
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	function initEditValues() {
		if (project) {
			editValues = {
				title: project.title || '',
				slug: project.slug || '',
				short_description: project.short_description || '',
				description: project.description || '',
				funding_goal: project.funding_goal || '',
				image_url: project.image_url || '',
				video_url: project.video_url || '',
				project_type: project.project_type || 'crowdfunding'
			};
		}
	}

	function toggleEditMode() {
		editMode = !editMode;
		if (!editMode) {
			editingField = null;
			initEditValues();
		}
	}

	function startEditingField(field) {
		if (!editMode || !canEdit) return;
		editingField = field;
	}

	function cancelFieldEdit() {
		editingField = null;
		initEditValues();
	}

	async function saveField(field) {
		saving = true;
		error = null;
		success = null;
		try {
			let value = editValues[field];

			// Parse number for funding_goal
			if (field === 'funding_goal') {
				value = value ? parseFloat(value) : null;
			} else if (typeof value === 'string') {
				value = value.trim() || null;
			}

			const updateData = { [field]: value };
			project = await updateProject(project.slug, updateData);

			// If slug changed, navigate to new URL
			if (field === 'slug' && value !== slug) {
				goto(`/projects/${project.slug}`, { replaceState: true });
			}

			success = $t('project.updated');
			editingField = null;
			initEditValues();

			// Clear success message after 3 seconds
			setTimeout(() => {
				success = null;
			}, 3000);
		} catch (e) {
			error = e.message;
		} finally {
			saving = false;
		}
	}

	async function handleSubmit() {
		submitting = true;
		error = null;
		try {
			project = await submitProject(project.slug);
			editMode = false;
		} catch (e) {
			error = e.message;
		} finally {
			submitting = false;
		}
	}

	async function handleDelete() {
		deleting = true;
		error = null;
		try {
			await deleteProject(project.slug);
			showDeleteConfirm = false;
			deleteConfirmSlug = '';
			goto('/profile');
		} catch (e) {
			error = e.message;
			showDeleteConfirm = false;
			deleteConfirmSlug = '';
			deleting = false;
		}
	}

	function openDuplicateConfirm() {
		showActionsMenu = false;
		showDuplicateConfirm = true;
	}

	async function handleDuplicate() {
		duplicating = true;
		error = null;
		showDuplicateConfirm = false;
		try {
			const newProject = await duplicateProject(project.slug);
			if (newProject?.slug) {
				await goto(`/projects/${newProject.slug}`);
			} else {
				error = 'Failed to duplicate project';
				duplicating = false;
			}
		} catch (e) {
			error = e.message;
			duplicating = false;
		}
	}

	function toggleActionsMenu() {
		showActionsMenu = !showActionsMenu;
	}

	function closeActionsMenu() {
		showActionsMenu = false;
	}

	let slugCopied = false;
	async function copySlugToClipboard() {
		try {
			await navigator.clipboard.writeText(project.slug);
			slugCopied = true;
			setTimeout(() => {
				slugCopied = false;
			}, 2000);
		} catch (e) {
			console.error('Failed to copy slug:', e);
		}
	}

	// Local wrapper for formatDate with day included (used in project detail)
	function formatProjectDate(dateStr) {
		return formatDate(dateStr, { includeDay: true });
	}

	function handleKeydown(event, field) {
		if (event.key === 'Enter' && !event.shiftKey && field !== 'description') {
			event.preventDefault();
			saveField(field);
		} else if (event.key === 'Escape') {
			cancelFieldEdit();
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
	{:else if error && !project}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded">
			{error}
		</div>
	{:else if project}
		{#if error}
			<div class="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded">
				{error}
			</div>
		{/if}

		{#if success}
			<div class="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 px-4 py-3 rounded">
				{success}
			</div>
		{/if}

		<!-- Project View with Inline Editing -->
		<div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
			<!-- Project Image -->
			{#if editMode && editingField === 'image_url'}
				<div class="p-4 bg-gray-50 dark:bg-gray-700/50">
					<!-- Current Image Preview -->
					{#if project.image_url}
						<div class="mb-4">
							<img
								src={getImageUrl(project.image_url)}
								alt={project.title}
								class="w-full h-48 object-cover rounded-lg"
							/>
						</div>
					{/if}

					<!-- Upload Button -->
					<div class="mb-4">
						<input
							type="file"
							accept="image/*"
							bind:this={imageInput}
							on:change={handleImageUpload}
							class="hidden"
							id="project-image-input"
						/>
						<div class="flex items-center gap-3">
							<button
								on:click={() => imageInput?.click()}
								disabled={imageUploading}
								class="px-4 py-2 bg-[#06E481] text-[#304b50] font-semibold rounded-md hover:bg-[#05b667] transition-colors disabled:opacity-50 flex items-center gap-2"
							>
								{#if imageUploading}
									<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
								{:else}
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
									</svg>
								{/if}
								{$t('project.uploadImage')}
							</button>

							{#if project.image_url}
								<button
									on:click={handleDeleteImage}
									disabled={imageUploading}
									class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors disabled:opacity-50"
								>
									{$t('project.deleteImage')}
								</button>
							{/if}
						</div>
						<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">{$t('project.imageHint')}</p>
					</div>

					<!-- Or use URL -->
					<div class="border-t border-gray-200 dark:border-gray-600 pt-4">
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							{$t('project.orEnterUrl')}
						</label>
						<input
							type="url"
							bind:value={editValues.image_url}
							on:keydown={(e) => handleKeydown(e, 'image_url')}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-[#06E481] focus:border-[#06E481] dark:bg-gray-700 dark:text-white"
							placeholder="https://..."
						/>
						<div class="mt-2 flex gap-2">
							<button
								on:click={() => saveField('image_url')}
								disabled={saving}
								class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
							>
								{saving ? $t('project.saving') : $t('common.save')}
							</button>
							<button
								on:click={cancelFieldEdit}
								class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
							>
								{$t('common.cancel')}
							</button>
						</div>
					</div>
				</div>
			{:else}
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div
					class="relative group {editMode && canEdit ? 'cursor-pointer' : ''}"
					on:click={() => startEditingField('image_url')}
				>
					{#if project.image_url}
						<img
							src={getImageUrl(project.image_url)}
							alt={project.title}
							class="w-full h-64 object-cover"
						/>
					{:else}
						<div class="w-full h-64 bg-gradient-to-br from-[#304b50] to-[#06E481] flex items-center justify-center">
							<svg class="h-24 w-24 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
							</svg>
						</div>
					{/if}
					{#if editMode && canEdit}
						<div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 flex items-center justify-center transition-all">
							<div class="opacity-0 group-hover:opacity-100 transition-opacity">
								<div class="bg-white dark:bg-gray-800 rounded-full p-2">
									<svg class="h-6 w-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
									</svg>
								</div>
							</div>
						</div>
					{/if}

					<!-- Actions Menu (Cog) - top right corner on image -->
					{#if (isOwner || isAdmin) && !editMode}
						<div class="absolute top-4 right-4">
							<div class="relative">
								<button
									on:click|stopPropagation={toggleActionsMenu}
									class="p-2 bg-white/90 dark:bg-gray-800/90 rounded-full shadow-lg hover:bg-white dark:hover:bg-gray-800 transition-colors"
									title={$t('project.actions')}
								>
									<svg class="h-5 w-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									</svg>
								</button>

								{#if showActionsMenu}
									<!-- svelte-ignore a11y_no_static_element_interactions -->
									<div
										class="fixed inset-0 z-40"
										on:click|stopPropagation={closeActionsMenu}
									></div>
									<div class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
										<div class="py-1">
											<!-- Duplicate -->
											<button
												on:click|stopPropagation={openDuplicateConfirm}
												class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
											>
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
												</svg>
												{$t('project.duplicate')}
											</button>

											<!-- Delete -->
											{#if (project.status === 'draft' && isOwner) || isAdmin}
												<button
													on:click|stopPropagation={() => { showActionsMenu = false; showDeleteConfirm = true; }}
													class="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2"
												>
													<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
													</svg>
													{$t('project.delete')}
												</button>
											{/if}
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}
				</div>
			{/if}

			<div class="p-6">
				<!-- Status Badge and Submit Button -->
				<div class="flex justify-between items-start mb-4">
					<div class="flex items-center gap-3">
						<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {getProjectTypeColor(project.project_type)}">
							{$t(`project.type.${project.project_type || 'crowdfunding'}`)}
						</span>
						<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium {getStatusColor(project.status)}">
							{$t(`project.status.${project.status}`)}
						</span>
						{#if project.ai_generated}
							<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400">
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
								</svg>
								{$t('project.aiGenerated')}
							</span>
						{/if}

						<!-- Submit button next to draft badge -->
						{#if project.status === 'draft' && isOwner}
							<button
								on:click={handleSubmit}
								disabled={submitting}
								class="px-3 py-1 text-sm bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-md hover:bg-green-200 dark:hover:bg-green-900/50 disabled:opacity-50 transition-colors"
							>
								{submitting ? $t('project.submitting') : $t('project.submit')}
							</button>
						{/if}
					</div>

					<!-- Edit Mode Toggle -->
					{#if (isOwner || isAdmin) && canEdit}
						<button
							on:click={toggleEditMode}
							class="px-3 py-1 text-sm rounded-md transition-colors {editMode
								? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50'
								: 'bg-[#06E481]/20 dark:bg-[#06E481]/20 text-[#304b50] dark:text-[#06E481] hover:bg-[#06E481]/30 dark:hover:bg-[#06E481]/30'}"
						>
							{#if editMode}
								{$t('project.editModeOff')}
							{:else}
								{$t('project.editModeOn')}
							{/if}
						</button>
					{/if}
				</div>

				<!-- Title -->
				{#if editMode && editingField === 'title'}
					<div class="mb-4">
						<input
							type="text"
							bind:value={editValues.title}
							on:keydown={(e) => handleKeydown(e, 'title')}
							class="w-full text-3xl font-bold px-2 py-1 border border-[#06E481] rounded-md dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-[#06E481]"
							autofocus
						/>
						<div class="mt-2 flex gap-2">
							<button
								on:click={() => saveField('title')}
								disabled={saving}
								class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
							>
								{saving ? $t('project.saving') : $t('common.save')}
							</button>
							<button
								on:click={cancelFieldEdit}
								class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
							>
								{$t('common.cancel')}
							</button>
						</div>
					</div>
				{:else}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="group flex items-start gap-2 mb-2 {editMode && canEdit ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 -mx-2 px-2 py-1 rounded' : ''}"
						on:click={() => startEditingField('title')}
					>
						<h1 class="text-3xl font-bold text-[#304b50] dark:text-white">
							{project.title}
						</h1>
						{#if editMode && canEdit}
							<svg class="h-5 w-5 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity mt-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
							</svg>
						{/if}
					</div>
				{/if}

				<!-- Slug (only shown in edit mode) -->
				{#if editMode}
					{#if editingField === 'slug'}
						<div class="mb-4">
							<label class="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{$t('project.slug')}</label>
							<input
								type="text"
								bind:value={editValues.slug}
								on:keydown={(e) => handleKeydown(e, 'slug')}
								class="w-full px-2 py-1 border border-[#06E481] rounded-md dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-[#06E481] text-sm"
							/>
							<div class="mt-2 flex gap-2">
								<button
									on:click={() => saveField('slug')}
									disabled={saving}
									class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
								>
									{saving ? $t('project.saving') : $t('common.save')}
								</button>
								<button
									on:click={cancelFieldEdit}
									class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
								>
									{$t('common.cancel')}
								</button>
							</div>
						</div>
					{:else}
						<!-- svelte-ignore a11y_click_events_have_key_events -->
						<!-- svelte-ignore a11y_no_static_element_interactions -->
						<div
							class="group flex items-center gap-2 mb-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 -mx-2 px-2 py-1 rounded"
							on:click={() => startEditingField('slug')}
						>
							<span class="text-sm text-gray-500 dark:text-gray-400">{$t('project.slug')}:</span>
							<span class="text-sm text-gray-600 dark:text-gray-400">{project.slug}</span>
							<svg class="h-4 w-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
							</svg>
						</div>
					{/if}
				{/if}

				<!-- Project Type (only in edit mode) -->
				{#if editMode}
					{#if editingField === 'project_type'}
						<div class="mb-4">
							<label class="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{$t('project.type')}</label>
							<select
								bind:value={editValues.project_type}
								class="w-full px-2 py-1 border border-[#06E481] rounded-md dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-[#06E481] text-sm"
							>
								<option value="crowdfunding">{$t('project.type.crowdfunding')}</option>
								<option value="fundraising">{$t('project.type.fundraising')}</option>
								<option value="private">{$t('project.type.private')}</option>
							</select>
							<div class="mt-2 flex gap-2">
								<button
									on:click={() => saveField('project_type')}
									disabled={saving}
									class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
								>
									{saving ? $t('project.saving') : $t('common.save')}
								</button>
								<button
									on:click={cancelFieldEdit}
									class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
								>
									{$t('common.cancel')}
								</button>
							</div>
						</div>
					{:else}
						<!-- svelte-ignore a11y_click_events_have_key_events -->
						<!-- svelte-ignore a11y_no_static_element_interactions -->
						<div
							class="group flex items-center gap-2 mb-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 -mx-2 px-2 py-1 rounded"
							on:click={() => startEditingField('project_type')}
						>
							<span class="text-sm text-gray-500 dark:text-gray-400">{$t('project.type')}:</span>
							<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {getProjectTypeColor(project.project_type)}">
								{$t(`project.type.${project.project_type || 'crowdfunding'}`)}
							</span>
							<svg class="h-4 w-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
							</svg>
						</div>
					{/if}
				{/if}

				<!-- Owner and Date -->
				<div class="text-gray-600 dark:text-gray-400 text-sm mb-6">
					{#if project.owner}
						{$t('project.by')}
						<a
							href="/profile/{project.owner.profile_slug}"
							class="text-[#304b50] dark:text-[#06E481] hover:underline font-medium"
						>
							{project.owner.full_name || project.owner.email}
						</a>
					{/if}
					<span class="mx-2">•</span>
					{formatProjectDate(project.created_at)}
				</div>

				<!-- Funding Goal -->
				{#if editMode && editingField === 'funding_goal'}
					<div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-6">
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							{$t('project.fundingGoal')} (EUR)
						</label>
						<input
							type="number"
							bind:value={editValues.funding_goal}
							on:keydown={(e) => handleKeydown(e, 'funding_goal')}
							min="0"
							step="1"
							class="w-full px-3 py-2 border border-[#06E481] rounded-md shadow-sm focus:ring-[#06E481] focus:border-[#06E481] dark:bg-gray-700 dark:text-white"
						/>
						<div class="mt-2 flex gap-2">
							<button
								on:click={() => saveField('funding_goal')}
								disabled={saving}
								class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
							>
								{saving ? $t('project.saving') : $t('common.save')}
							</button>
							<button
								on:click={cancelFieldEdit}
								class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
							>
								{$t('common.cancel')}
							</button>
						</div>
					</div>
				{:else if project.funding_goal || editMode}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-6 group {editMode && canEdit ? 'cursor-pointer hover:ring-2 hover:ring-[#06E481] dark:hover:ring-[#05b667]' : ''}"
						on:click={() => startEditingField('funding_goal')}
					>
						{#if project.funding_goal}
							<div class="flex justify-between items-end mb-2">
								<div>
									<div class="text-2xl font-bold text-[#304b50] dark:text-white">
										{formatCurrency(project.funding_current)}
									</div>
									<div class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
										{$t('project.goal')}: {formatCurrency(project.funding_goal)}
										{#if editMode && canEdit}
											<svg class="h-4 w-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
											</svg>
										{/if}
									</div>
								</div>
								<div class="text-right">
									<div class="text-2xl font-bold text-[#304b50] dark:text-[#06E481]">
										{calculateProgress(project.funding_current, project.funding_goal)}%
									</div>
									<div class="text-sm text-gray-600 dark:text-gray-400">
										{$t('project.funded')}
									</div>
								</div>
							</div>
							<div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-3">
								<div
									class="bg-[#06E481] h-3 rounded-full transition-all"
									style="width: {calculateProgress(project.funding_current, project.funding_goal)}%"
								></div>
							</div>
						{:else if editMode}
							<div class="text-gray-500 dark:text-gray-400 flex items-center gap-2">
								<span>{$t('project.fundingGoal')}: {$t('project.notSet')}</span>
								<svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
								</svg>
							</div>
						{/if}
					</div>
				{/if}

				<!-- Support Button -->
				{#if project.status === 'financing'}
					<button
						class="w-full mb-6 py-4 px-6 font-bold text-lg rounded-lg transition-colors shadow-lg hover:shadow-xl
							{project.project_type === 'crowdfunding' ? 'bg-[#06E481] text-[#304b50] hover:bg-[#05b667]' : ''}
							{project.project_type === 'fundraising' ? 'bg-[#FF85FF] text-white hover:bg-[#e070e0]' : ''}
							{project.project_type === 'private' ? 'bg-[#FFC21C] text-[#304b50] hover:bg-[#e0aa18]' : ''}"
					>
						{$t('project.support')}
					</button>
				{/if}

				<!-- Short Description -->
				{#if editMode && editingField === 'short_description'}
					<div class="mb-6">
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							{$t('project.shortDescription')}
						</label>
						<textarea
							bind:value={editValues.short_description}
							rows="2"
							maxlength="500"
							class="w-full px-3 py-2 border border-[#06E481] rounded-md shadow-sm focus:ring-[#06E481] focus:border-[#06E481] dark:bg-gray-700 dark:text-white"
						></textarea>
						<div class="mt-2 flex gap-2">
							<button
								on:click={() => saveField('short_description')}
								disabled={saving}
								class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
							>
								{saving ? $t('project.saving') : $t('common.save')}
							</button>
							<button
								on:click={cancelFieldEdit}
								class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
							>
								{$t('common.cancel')}
							</button>
						</div>
					</div>
				{:else if project.short_description || editMode}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="group mb-6 {editMode && canEdit ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 -mx-2 px-2 py-2 rounded' : ''}"
						on:click={() => startEditingField('short_description')}
					>
						{#if project.short_description}
							<p class="text-lg text-gray-700 dark:text-gray-300 flex items-start gap-2">
								<span>{project.short_description}</span>
								{#if editMode && canEdit}
									<svg class="h-4 w-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
									</svg>
								{/if}
							</p>
						{:else if editMode}
							<p class="text-gray-500 dark:text-gray-400 italic flex items-center gap-2">
								<span>{$t('project.shortDescription')}: {$t('project.notSet')}</span>
								<svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
								</svg>
							</p>
						{/if}
					</div>
				{/if}

				<!-- Full Description -->
				{#if editMode && editingField === 'description'}
					<div class="mb-6">
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							{$t('project.description')}
						</label>
						<textarea
							bind:value={editValues.description}
							rows="10"
							class="w-full px-3 py-2 border border-[#06E481] rounded-md shadow-sm focus:ring-[#06E481] focus:border-[#06E481] dark:bg-gray-700 dark:text-white"
						></textarea>
						<div class="mt-2 flex gap-2">
							<button
								on:click={() => saveField('description')}
								disabled={saving}
								class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
							>
								{saving ? $t('project.saving') : $t('common.save')}
							</button>
							<button
								on:click={cancelFieldEdit}
								class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
							>
								{$t('common.cancel')}
							</button>
						</div>
					</div>
				{:else if project.description || editMode}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="prose dark:prose-invert max-w-none group {editMode && canEdit ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 -mx-2 px-2 py-2 rounded' : ''}"
						on:click={() => startEditingField('description')}
					>
						<div class="flex items-start gap-2">
							<h2 class="text-xl font-semibold text-[#304b50] dark:text-white mb-4">
								{$t('project.description')}
							</h2>
							{#if editMode && canEdit}
								<svg class="h-4 w-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
								</svg>
							{/if}
						</div>
						{#if project.description}
							<div class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
								{project.description}
							</div>
						{:else if editMode}
							<p class="text-gray-500 dark:text-gray-400 italic">{$t('project.notSet')}</p>
						{/if}
					</div>
				{/if}

				<!-- Video -->
				{#if editMode && editingField === 'video_url'}
					<div class="mt-6">
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							{$t('project.videoUrl')}
						</label>
						<input
							type="url"
							bind:value={editValues.video_url}
							on:keydown={(e) => handleKeydown(e, 'video_url')}
							class="w-full px-3 py-2 border border-[#06E481] rounded-md shadow-sm focus:ring-[#06E481] focus:border-[#06E481] dark:bg-gray-700 dark:text-white"
							placeholder="https://..."
						/>
						<div class="mt-2 flex gap-2">
							<button
								on:click={() => saveField('video_url')}
								disabled={saving}
								class="px-3 py-1 text-sm bg-[#06E481] text-[#304b50] font-semibold rounded hover:bg-[#05b667] disabled:opacity-50"
							>
								{saving ? $t('project.saving') : $t('common.save')}
							</button>
							<button
								on:click={cancelFieldEdit}
								class="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-500"
							>
								{$t('common.cancel')}
							</button>
						</div>
					</div>
				{:else if project.video_url || editMode}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="mt-6 group {editMode && canEdit ? 'cursor-pointer' : ''}"
						on:click={() => startEditingField('video_url')}
					>
						<div class="flex items-center gap-2 mb-4">
							<h2 class="text-xl font-semibold text-[#304b50] dark:text-white">Video</h2>
							{#if editMode && canEdit}
								<svg class="h-4 w-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
								</svg>
							{/if}
						</div>
						{#if project.video_url}
							<div class="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
								<iframe
									src={project.video_url}
									title="Project video"
									class="w-full h-full"
									frameborder="0"
									allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
									allowfullscreen
								></iframe>
							</div>
						{:else if editMode}
							<p class="text-gray-500 dark:text-gray-400 italic">{$t('project.notSet')}</p>
						{/if}
					</div>
				{/if}
			</div>
		</div>

		<!-- Delete Confirmation Modal -->
		{#if showDeleteConfirm}
			<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
				<div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
					<h3 class="text-lg font-semibold text-[#304b50] dark:text-white mb-4">
						{$t('project.delete')}
					</h3>
					<p class="text-gray-600 dark:text-gray-400 mb-4">
						{$t('project.confirmDelete')}
					</p>

					<!-- Slug confirmation for all users -->
					<div class="mb-6">
						<p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
							{@html $t('project.confirmDeleteSlug').replace('{slug}', `<span class="font-mono font-semibold text-[#304b50] dark:text-white">${project.slug}</span>`)}
							<button
								type="button"
								on:click={copySlugToClipboard}
								class="ml-1 inline-flex items-center text-gray-400 hover:text-[#304b50] dark:hover:text-white transition-colors"
								title="Copy to clipboard"
							>
								{#if slugCopied}
									<svg class="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
									</svg>
								{:else}
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
									</svg>
								{/if}
							</button>
						</p>
						<input
							type="text"
							bind:value={deleteConfirmSlug}
							placeholder={project.slug}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-red-500 focus:border-red-500 dark:bg-gray-700 dark:text-white"
						/>
					</div>

					<div class="flex gap-4">
						<button
							on:click={handleDelete}
							disabled={deleting || deleteConfirmSlug !== project.slug}
							class="flex-1 px-4 py-2 bg-red-600 text-white font-medium rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
						>
							{deleting ? $t('common.loading') : $t('common.delete')}
						</button>
						<button
							on:click={() => { showDeleteConfirm = false; deleteConfirmSlug = ''; }}
							class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
						>
							{$t('common.cancel')}
						</button>
					</div>
				</div>
			</div>
		{/if}

		<!-- Duplicate Confirmation Modal -->
		{#if showDuplicateConfirm}
			<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
				<div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
					<h3 class="text-lg font-semibold text-[#304b50] dark:text-white mb-4">
						{$t('project.duplicate')}
					</h3>
					<p class="text-gray-600 dark:text-gray-400 mb-6">
						{$t('project.confirmDuplicate')}
					</p>

					<div class="flex gap-4">
						<button
							on:click={handleDuplicate}
							disabled={duplicating}
							class="flex-1 px-4 py-2 bg-[#06E481] text-[#304b50] font-semibold rounded-md hover:bg-[#05b667] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
						>
							{duplicating ? $t('common.loading') : $t('project.duplicate')}
						</button>
						<button
							on:click={() => { showDuplicateConfirm = false; }}
							class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
						>
							{$t('common.cancel')}
						</button>
					</div>
				</div>
			</div>
		{/if}
	{/if}
</div>
