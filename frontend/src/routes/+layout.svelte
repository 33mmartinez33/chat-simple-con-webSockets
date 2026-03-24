<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import { page } from '$app/state';
	import { goto } from '$app/navigation';

    let { children } = $props();

    const sinMenu = ['/', '/login', '/sign_in'];
    let mostrarMenu = $derived(!sinMenu.includes(page.url.pathname));
	let id_usuario = $derived(page.params.id_usuario);
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

{#if mostrarMenu}
    <nav>
        <button class="btn-menu" onclick={() => {
		console.log('id_usuario:', id_usuario);
		goto(`/usuarios/${id_usuario}`);
		}}>
            <img src="/assets/img/logo_pequeno.JPG" alt="Nexus" />
        </button>
    </nav>
{/if}
{@render children()}