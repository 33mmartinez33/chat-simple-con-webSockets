<script lang="ts">
	import { goto } from '$app/navigation';
    import { tick } from 'svelte';

    type Mensajes = {
        id_mensaje: number,
        contenido: string,
        username: string,
        id_usuario_emisor: number,
        fecha: Date
    };

    type Amigo = {
        id_amigo: number,
        email: string,
        username: string,
        fecha_de_nacimiento: Date,
        fecha_de_alta: Date
    };

    type Canal = {
		id_canal: number;
        nombre: string
    }

    let { data } = $props();
    let mensajes: Mensajes[] = $state([]);
    let infoAmigo : Amigo = $derived(data.infoAmigo ?? {});
    let canales: Canal[] = $derived(data.canales ?? []);
    let amigos: Amigo[] = $derived(data.amigos ?? []);
    let id_usuario: number = $derived(Number(data.id_usuario ?? {}));

    let contenido = $state("");

    let ws: WebSocket;
    let listaMensajes: HTMLDivElement;

        async function scrollAbajo() {
        await tick(); // espera a que svelte actualice el DOM
        listaMensajes.scrollTop = listaMensajes.scrollHeight;
    }

    function enviarMensaje() {
        if (!contenido.trim()) return;

        // añadir localmente de forma inmediata
        mensajes = [...mensajes, {
        id_mensaje: -1,
        contenido,
        username: data.infoUser.username,
        id_usuario_emisor: Number(data.id_usuario),
        fecha: new Date()
    }];

        ws.send(JSON.stringify({ contenido }));
        contenido = '';
        scrollAbajo();
    }
    
    $effect(() => {
    mensajes = data.mensajes ?? [];
    infoAmigo = data.infoAmigo ?? {};

    // cierra el ws anterior y abre uno nuevo
    if (ws) ws.close();
    
    ws = new WebSocket(`ws://localhost:8001/ws/usuarios/${data.id_usuario}/amigos/${data.id_usuario2}`);
    
    ws.onmessage = (event) => {
        const mensaje = JSON.parse(event.data);
        if (mensaje.id_usuario_emisor === Number(data.id_usuario)) {
            mensajes = mensajes.map(m => m.id_mensaje === -1 ? mensaje : m);
        } else {
            mensajes = [...mensajes, mensaje];
        }
        scrollAbajo();
    };

    scrollAbajo();

    return () => ws.close(); // cleanup cuando cambia data o se destruye
});

    function irCanal(id_canal : number){
        goto (`/usuarios/${id_usuario}/canales/${id_canal}`);
    }
    function irAmigo(id_usuario2: number){
        goto (`/usuarios/${id_usuario}/amigos/${id_usuario2}`);
    }

</script>

<aside class="sidebar">
    <ul class="ul-sidebar">
        <li>
            <p class = "p-sidebar">Canales</p>
            <ul>
                {#each canales as canal}
                    <li class="li-sidebar">
                        <button class="btn-sidebar" onclick={() => {irCanal(canal.id_canal)}}>{canal.nombre}</button>
                    </li>
                {/each}
            </ul>
        </li>
        <li>
            <p class = "p-sidebar">Amigos</p>
            <ul>
                {#each amigos as amigo}
                    <li class="li-sidebar">
                        <button  class="btn-sidebar" onclick={() => {irAmigo(amigo.id_amigo)}}>{amigo.username}</button>
                    </li>    
                {/each}
            </ul>
        </li>
    </ul>
    <!-- Info del amigo -->
    <!-- avatar por defecto -->
    <!-- nombre de usuario  -->
    <!-- fecha de amistad -->
</aside>


<main>
<h1>{infoAmigo.username}</h1>
    <div>
        <div id = "listaMensajes" bind:this={listaMensajes}>
            {#each mensajes as mensaje}
                <div id="mensaje">
                    <ul>
                    <!-- antes de mostrar el infoAmigo.username deberiamos comporbar si es el amigo el que envio el mensaje, comprobando por id, si es su id se mostrara su username si no lo es se mostrara el username del usuario  -->
                        <li id= "msg-usrname">{mensaje.username}</li>
                        <li>{new Date(mensaje.fecha).toLocaleDateString('es-ES')} {new Date(mensaje.fecha).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</li>
                    </ul>
                    <p>{mensaje.contenido}</p>
                </div>
                <hr>
            {/each}
        </div>
        <input type="text" placeholder="Escribe un mensaje..." onkeydown={(e) => { if (e.key === 'Enter') enviarMensaje() }} bind:value={contenido}>
    </div>
</main>

<style>
    aside {
        width: 250px;
        flex-shrink: 0;
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        background: var(--bg-secondary);
        padding: 1rem;
        padding-top: 60px;
    }

    .p-sidebar {
        margin-top: 40px;
        margin-bottom: 12px;
        color: var(--accent-secondary);
        font-weight: bold;
        font-size: larger;
    }

    .ul-sidebar {
        display: flex;
        flex-direction: column;
    }

    .li-sidebar {
        display: flex;
        flex-direction: column;
        text-align: left;
        width: fit-content;
    }

    .btn-sidebar {
        text-align: left;
        cursor: pointer;
        width: auto;
        color: var(--text-secondary);
        padding: 4px 8px;
        background: none;
        border: none;
    }

    main {
        margin-left: 250px;
    }

    div {
        margin-top: 1%;
        height: 800px;
        border-radius: 40px;
        border: 1px solid var(--accent-primary);
        margin: 1% clamp(20px, 10%, 200px) 0% clamp(20px, 10%, 200px);
        background-color: var(--bg-primary);
        padding: 12px 12px;
        display: flex;
        flex-direction: column;
    }

    #listaMensajes {
        display: block;
        flex: 1;
        overflow-y: auto;
        border-radius: 28px 28px 0 0;
        border: none;
        margin: 0;
        background-color: var(--bg-primary);
        padding: 0;
        scrollbar-color: var(--border-accent) transparent;
        scrollbar-width: thin;
    }

    #listaMensajes::-webkit-scrollbar {
        width: 6px;
    }

    #listaMensajes::-webkit-scrollbar-track {
        background: transparent;
    }

    #listaMensajes::-webkit-scrollbar-thumb {
        background: var(--border-accent);
        border-radius: 10px;
    }

    #listaMensajes::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }

    #mensaje {
        display: block;
        margin: auto;
        margin-top: 1%;
        height: auto;
        border: none;
    }

    #msg-usrname {
        color: var(--accent-primary);
        font-weight: bold;
        font-size: larger;
    }

    ul {
        color: var(--text-secondary);
        text-align: justify;
    }

    li {
        display: inline-block;
    }

    p {
        text-align: justify;
    }

    hr {
        color: var(--border-normal);
        margin-left: 12px;
        margin-right: 12px;
    }

    input {
        width: 99%;
        flex-shrink: 0;
    }
</style>