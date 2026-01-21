<script>
	import '../app.css';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { isAuthenticated, isAdmin, logout } from '$lib/api';

	let authenticated = false;
	let admin = false;

	onMount(() => {
		authenticated = isAuthenticated();
		admin = isAdmin();
	});

	async function handleLogout() {
		try {
			await logout();
			goto('/login');
		} catch (error) {
			console.error('Logout failed:', error);
		}
	}
</script>

<div class="min-h-screen bg-gray-50">
	<nav class="bg-white shadow-sm">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<div class="flex items-center">
					<a href="/" class="text-xl font-bold text-gray-800">Nutzerverwaltung</a>
				</div>

				<div class="flex items-center space-x-4">
					{#if authenticated}
						<a href="/profile" class="text-gray-700 hover:text-blue-600">Profil</a>
						{#if admin}
							<a href="/admin" class="text-gray-700 hover:text-blue-600">Admin</a>
						{/if}
						<button on:click={handleLogout} class="text-gray-700 hover:text-blue-600">
							Logout
						</button>
					{:else}
						<a href="/login" class="text-gray-700 hover:text-blue-600">Login</a>
						<a href="/register" class="text-gray-700 hover:text-blue-600">Registrieren</a>
					{/if}
				</div>
			</div>
		</div>
	</nav>

	<main>
		<slot />
	</main>
</div>
