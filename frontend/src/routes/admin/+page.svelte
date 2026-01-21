<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listUsers, updateUser, deleteUser, isAuthenticated, isAdmin } from '$lib/api';

	let users = [];
	let loading = true;
	let error = '';
	let success = '';

	onMount(async () => {
		if (!isAuthenticated()) {
			goto('/login');
			return;
		}

		if (!isAdmin()) {
			goto('/profile');
			return;
		}

		await loadUsers();
	});

	async function loadUsers() {
		loading = true;
		error = '';
		try {
			users = await listUsers();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function toggleActive(userId, currentStatus) {
		error = '';
		success = '';
		try {
			await updateUser(userId, { is_active: !currentStatus });
			success = 'Benutzerstatus aktualisiert';
			await loadUsers();
		} catch (err) {
			error = err.message;
		}
	}

	async function toggleAdmin(userId, currentStatus) {
		error = '';
		success = '';
		try {
			await updateUser(userId, { is_admin: !currentStatus });
			success = 'Admin-Status aktualisiert';
			await loadUsers();
		} catch (err) {
			error = err.message;
		}
	}

	async function handleDeleteUser(userId, email) {
		if (!confirm(`Möchten Sie den Benutzer ${email} wirklich löschen?`)) {
			return;
		}

		error = '';
		success = '';
		try {
			await deleteUser(userId);
			success = 'Benutzer gelöscht';
			await loadUsers();
		} catch (err) {
			error = err.message;
		}
	}
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<h1 class="text-3xl font-bold text-gray-800 mb-8">Admin-Panel</h1>

	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{/if}

	{#if success}
		<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
			{success}
		</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">
			<p class="text-gray-600">Lädt...</p>
		</div>
	{:else}
		<div class="bg-white rounded-lg shadow-md overflow-hidden">
			<div class="px-6 py-4 border-b border-gray-200">
				<h2 class="text-xl font-semibold text-gray-800">Benutzerverwaltung</h2>
			</div>

			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								E-Mail
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Name
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Status
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Rolle
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								2FA
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Erstellt
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Aktionen
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each users as user}
							<tr>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
									{user.email}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
									{user.full_name || '-'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									{#if user.is_active}
										<span class="inline-block bg-green-100 text-green-800 px-2 py-1 rounded text-xs"
											>Aktiv</span
										>
									{:else}
										<span class="inline-block bg-red-100 text-red-800 px-2 py-1 rounded text-xs"
											>Inaktiv</span
										>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									{#if user.is_admin}
										<span class="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs"
											>Admin</span
										>
									{:else}
										<span class="inline-block bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs"
											>Nutzer</span
										>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
									{user.two_factor_enabled ? '✓' : '-'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{new Date(user.created_at).toLocaleDateString('de-DE')}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
									<button
										on:click={() => toggleActive(user.id, user.is_active)}
										class="text-blue-600 hover:text-blue-900"
									>
										{user.is_active ? 'Deaktivieren' : 'Aktivieren'}
									</button>
									<button
										on:click={() => toggleAdmin(user.id, user.is_admin)}
										class="text-purple-600 hover:text-purple-900"
									>
										{user.is_admin ? 'Admin entziehen' : 'Admin machen'}
									</button>
									<button
										on:click={() => handleDeleteUser(user.id, user.email)}
										class="text-red-600 hover:text-red-900"
									>
										Löschen
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<div class="mt-6 text-gray-600">
			<p>Gesamt: {users.length} Benutzer</p>
		</div>
	{/if}
</div>
