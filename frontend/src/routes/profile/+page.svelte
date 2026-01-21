<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getCurrentUser, updateProfile, setup2FA, verify2FA, disable2FA, isAuthenticated } from '$lib/api';

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
	});

	async function handleUpdateProfile() {
		error = '';
		success = '';

		if (newPassword && newPassword !== confirmPassword) {
			error = 'Passwörter stimmen nicht überein';
			return;
		}

		try {
			const updateData = { full_name: fullName };
			if (newPassword) {
				updateData.password = newPassword;
			}

			user = await updateProfile(updateData);
			success = 'Profil erfolgreich aktualisiert';
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
			success = '2FA erfolgreich aktiviert';
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
			success = '2FA erfolgreich deaktiviert';
			user.two_factor_enabled = false;
			twoFactorVerifyCode = '';
		} catch (err) {
			error = err.message;
		}
	}
</script>

{#if loading}
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
		<p class="text-center text-gray-600">Lädt...</p>
	</div>
{:else if user}
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
		<h1 class="text-3xl font-bold text-gray-800 mb-8">Profil</h1>

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

		<div class="bg-white rounded-lg shadow-md p-6 mb-6">
			<h2 class="text-xl font-semibold text-gray-800 mb-4">Account-Informationen</h2>
			<div class="space-y-3">
				<div>
					<span class="font-medium text-gray-700">E-Mail:</span>
					<span class="text-gray-600 ml-2">{user.email}</span>
				</div>
				<div>
					<span class="font-medium text-gray-700">Status:</span>
					{#if user.is_active}
						<span class="ml-2 inline-block bg-green-100 text-green-800 px-2 py-1 rounded text-sm"
							>Aktiv</span
						>
					{:else}
						<span class="ml-2 inline-block bg-red-100 text-red-800 px-2 py-1 rounded text-sm"
							>Inaktiv</span
						>
					{/if}
				</div>
				<div>
					<span class="font-medium text-gray-700">Rolle:</span>
					{#if user.is_admin}
						<span class="ml-2 inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm"
							>Admin</span
						>
					{:else}
						<span class="ml-2 inline-block bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm"
							>Nutzer</span
						>
					{/if}
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg shadow-md p-6 mb-6">
			<h2 class="text-xl font-semibold text-gray-800 mb-4">Profil bearbeiten</h2>

			<form on:submit|preventDefault={handleUpdateProfile}>
				<div class="mb-4">
					<label for="fullName" class="block text-gray-700 font-medium mb-2">Name</label>
					<input
						type="text"
						id="fullName"
						bind:value={fullName}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>

				<div class="mb-4">
					<label for="newPassword" class="block text-gray-700 font-medium mb-2"
						>Neues Passwort (optional)</label
					>
					<input
						type="password"
						id="newPassword"
						bind:value={newPassword}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>

				{#if newPassword}
					<div class="mb-6">
						<label for="confirmPassword" class="block text-gray-700 font-medium mb-2"
							>Passwort bestätigen</label
						>
						<input
							type="password"
							id="confirmPassword"
							bind:value={confirmPassword}
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>
				{/if}

				<button
					type="submit"
					class="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
				>
					Profil aktualisieren
				</button>
			</form>
		</div>

		<div class="bg-white rounded-lg shadow-md p-6">
			<h2 class="text-xl font-semibold text-gray-800 mb-4">Zwei-Faktor-Authentifizierung</h2>

			{#if user.two_factor_enabled}
				<div class="mb-4">
					<p class="text-green-600 mb-4">2FA ist aktiviert</p>
					<div class="mb-4">
						<label for="disableCode" class="block text-gray-700 font-medium mb-2"
							>Code eingeben zum Deaktivieren</label
						>
						<input
							type="text"
							id="disableCode"
							bind:value={twoFactorVerifyCode}
							placeholder="123456"
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>
					<button
						on:click={handleDisable2FA}
						class="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700"
					>
						2FA deaktivieren
					</button>
				</div>
			{:else}
				{#if !show2FASetup}
					<p class="text-gray-600 mb-4">2FA ist nicht aktiviert</p>
					<button
						on:click={handleSetup2FA}
						class="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
					>
						2FA einrichten
					</button>
				{:else}
					<div class="space-y-4">
						<p class="text-gray-700">Scanne diesen QR-Code mit deiner Authenticator-App:</p>
						{#if twoFactorQRCode}
							<img src={twoFactorQRCode} alt="QR Code" class="mx-auto" />
						{/if}
						<p class="text-sm text-gray-600">Oder gib diesen Code manuell ein:</p>
						<p class="font-mono text-sm bg-gray-100 p-2 rounded">{twoFactorSecret}</p>

						<div class="mb-4">
							<label for="verifyCode" class="block text-gray-700 font-medium mb-2"
								>Bestätigungs-Code eingeben</label
							>
							<input
								type="text"
								id="verifyCode"
								bind:value={twoFactorVerifyCode}
								placeholder="123456"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>

						<button
							on:click={handleVerify2FA}
							class="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
						>
							2FA aktivieren
						</button>
						<button
							on:click={() => (show2FASetup = false)}
							class="ml-2 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
						>
							Abbrechen
						</button>
					</div>
				{/if}
			{/if}
		</div>
	</div>
{/if}
