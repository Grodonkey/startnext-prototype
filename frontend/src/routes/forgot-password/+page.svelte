<script>
	import { requestPasswordReset } from '$lib/api';

	let email = '';
	let error = '';
	let success = false;
	let loading = false;

	async function handleSubmit() {
		error = '';
		success = false;
		loading = true;

		try {
			await requestPasswordReset(email);
			success = true;
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="bg-white rounded-lg shadow-md p-8">
		<h2 class="text-2xl font-bold text-gray-800 mb-6">Passwort vergessen</h2>

		{#if error}
			<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
				{error}
			</div>
		{/if}

		{#if success}
			<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
				Wenn die E-Mail-Adresse existiert, wurde ein Link zum Zurücksetzen des Passworts gesendet.
			</div>
		{:else}
			<p class="text-gray-600 mb-4">
				Geben Sie Ihre E-Mail-Adresse ein und wir senden Ihnen einen Link zum Zurücksetzen Ihres
				Passworts.
			</p>

			<form on:submit|preventDefault={handleSubmit}>
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

				<button
					type="submit"
					disabled={loading}
					class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
				>
					{loading ? 'Senden...' : 'Link senden'}
				</button>
			</form>
		{/if}

		<div class="mt-6 text-center">
			<a href="/login" class="text-blue-600 hover:underline">Zurück zum Login</a>
		</div>
	</div>
</div>
