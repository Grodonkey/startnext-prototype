<script>
	import { goto } from '$app/navigation';
	import { register } from '$lib/api';

	let email = '';
	let password = '';
	let confirmPassword = '';
	let fullName = '';
	let error = '';
	let loading = false;

	async function handleRegister() {
		error = '';

		if (password !== confirmPassword) {
			error = 'Passwörter stimmen nicht überein';
			return;
		}

		if (password.length < 8) {
			error = 'Passwort muss mindestens 8 Zeichen lang sein';
			return;
		}

		loading = true;

		try {
			await register(email, password, fullName);
			goto('/login');
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="bg-white rounded-lg shadow-md p-8">
		<h2 class="text-2xl font-bold text-gray-800 mb-6">Registrieren</h2>

		{#if error}
			<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
				{error}
			</div>
		{/if}

		<form on:submit|preventDefault={handleRegister}>
			<div class="mb-4">
				<label for="email" class="block text-gray-700 font-medium mb-2">E-Mail</label>
				<input
					type="email"
					id="email"
					bind:value={email}
					required
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>

			<div class="mb-4">
				<label for="fullName" class="block text-gray-700 font-medium mb-2">Name (optional)</label>
				<input
					type="text"
					id="fullName"
					bind:value={fullName}
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>

			<div class="mb-4">
				<label for="password" class="block text-gray-700 font-medium mb-2">Passwort</label>
				<input
					type="password"
					id="password"
					bind:value={password}
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
				{loading ? 'Registrieren...' : 'Registrieren'}
			</button>
		</form>

		<div class="mt-6 text-center">
			<p class="text-gray-600">
				Bereits registriert?
				<a href="/login" class="text-blue-600 hover:underline">Anmelden</a>
			</p>
		</div>
	</div>
</div>
