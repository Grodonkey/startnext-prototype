<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { confirmPasswordReset } from '$lib/api';

	let token = '';
	let newPassword = '';
	let confirmPassword = '';
	let error = '';
	let success = false;
	let loading = false;

	onMount(() => {
		token = $page.url.searchParams.get('token') || '';
		if (!token) {
			error = 'Ungültiger oder fehlender Reset-Token';
		}
	});

	async function handleSubmit() {
		error = '';

		if (newPassword !== confirmPassword) {
			error = 'Passwörter stimmen nicht überein';
			return;
		}

		if (newPassword.length < 8) {
			error = 'Passwort muss mindestens 8 Zeichen lang sein';
			return;
		}

		loading = true;

		try {
			await confirmPasswordReset(token, newPassword);
			success = true;
			setTimeout(() => goto('/login'), 2000);
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="bg-white rounded-lg shadow-md p-8">
		<h2 class="text-2xl font-bold text-gray-800 mb-6">Neues Passwort setzen</h2>

		{#if error}
			<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
				{error}
			</div>
		{/if}

		{#if success}
			<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
				Passwort erfolgreich zurückgesetzt. Sie werden zum Login weitergeleitet...
			</div>
		{:else if token}
			<form on:submit|preventDefault={handleSubmit}>
				<div class="mb-4">
					<label for="newPassword" class="block text-gray-700 font-medium mb-2"
						>Neues Passwort</label
					>
					<input
						type="password"
						id="newPassword"
						bind:value={newPassword}
						required
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>

				<div class="mb-6">
					<label for="confirmPassword" class="block text-gray-700 font-medium mb-2"
						>Passwort bestätigen</label
					>
					<input
						type="password"
						id="confirmPassword"
						bind:value={confirmPassword}
						required
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>

				<button
					type="submit"
					disabled={loading}
					class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
				>
					{loading ? 'Speichern...' : 'Passwort zurücksetzen'}
				</button>
			</form>
		{/if}

		<div class="mt-6 text-center">
			<a href="/login" class="text-blue-600 hover:underline">Zurück zum Login</a>
		</div>
	</div>
</div>
