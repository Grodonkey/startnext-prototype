<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/api';

	onMount(() => {
		if (isAuthenticated()) {
			goto('/profile');
		} else {
			goto('/login');
		}
	});
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="text-center">
		<h1 class="text-4xl font-bold text-gray-800 mb-4">Willkommen zur Nutzerverwaltung</h1>
		<p class="text-gray-600 mb-8">Melden Sie sich an oder registrieren Sie sich, um fortzufahren.</p>
	</div>
</div>
