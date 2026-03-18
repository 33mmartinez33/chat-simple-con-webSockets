<script lang="ts">
    type Mensajes = {
        id_mensaje: number,
        contenido: string,
        id_usuario_emisor: number,
        fecha: Date
    }

    let { data } = $props();
    let mensajes: Mensajes[] = $derived(data.mensajes ?? [])
</script>

<main>
<!-- Boton menu Nexus arriba izquierda-->
<!-- Barra superior -->
<!-- Centro mensajes -->
<!-- Abajo input para escribir mensajes -->
</main>

<style>

</style>