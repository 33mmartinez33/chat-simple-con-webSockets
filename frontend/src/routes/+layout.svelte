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

<svelte:head>
    <link rel="icon" href={favicon} />
    <!-- <link rel="preload" href="assets/img/fondo_principal (1).jpg" as="image" fetchpriority= "high"> -->
</svelte:head>

{#if mostrarMenu}
    <nav>
        <button class="btn-menu" onclick={() => {
		goto(`/usuarios/${id_usuario}`);
		}}>
            <img src="/assets/img/logo-nexus-verde.JPG" alt="Nexus" />
        </button>
    </nav>
{/if}
{@render children()}