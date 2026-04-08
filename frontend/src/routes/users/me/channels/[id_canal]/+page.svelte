<script lang="ts">
	import Sidebar from '../../../../../components/Sidebar.svelte';

    type Canal = {
        id_canal: number;
        nombre: string;
        contenido_principal: string;
        rol: "PARTICIPANTE" | "ADMIN";
    };

    type Sala = {
        id_sala: number;
        tipo: string;
        nombre_sala: string;
    }

    type Usuario = {
        id_usuario: number;
        username: string;
        email: string;
        fecha_de_nacimiento: Date;
        fecha_de_alta: Date;
    }

    type Amigo = {
        id_amigo: number;
        username: string;
        email: string;
        fecha_amistad: string;
    }


    let { data } = $props();
    let infoUser: Usuario = $derived(data.infoUser ?? {});
    let canales: Canal[] = $derived(data.canales ?? []);
    let salas: Sala[] = $derived(data.salas ?? []);
    let amigos: Amigo[] = $derived(data.amigos ?? []);
    let canal: Canal = $derived(data.canal ?? {});

</script>

<main>
    <h1>{canal.nombre}</h1>
    <div class="contenido-principal">
    Post principal de bienvenida <br>
        {canal.contenido_principal}
    </div>
</main>

<Sidebar
    id_usuario={infoUser.id_usuario}
    canales={canales}
    amigos={amigos}
    canal={canal}
    salas={salas}
/>


<style>
    .contenido-principal {
        margin-top: 10%;
    }

</style>