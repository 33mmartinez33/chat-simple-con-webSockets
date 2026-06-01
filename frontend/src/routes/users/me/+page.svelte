<script lang="ts">
    import Sidebar from '../../../components/Sidebar.svelte';

    type Canal = {
        id_canal: number;
        nombre: string;
        id_usuario_dueno: number;
        contenido_principal: string;
    }

    type Amigo = {
        id_amigo: number;
        username: string;
        email: string;
        fecha_amistad: string;
    }

    let { data } = $props();
    let canales: Canal[] = $derived(data.canales ?? []);
    let amigos: Amigo[] = $derived(data.amigos ?? []);
</script>

<main>
    <h1>Bienvenido</h1>
    <p>Selecciona un canal o un amigo del panel lateral para comenzar.</p>
</main>

<Sidebar
    canales={canales}
    amigos={amigos}
/>

<style>
    main {
        margin-left: 250px;
        color: var(--text-primary);
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 25vh;
        text-align: center;
    }
</style>