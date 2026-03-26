<script lang="ts">
	import { goto } from '$app/navigation';
    import { tick } from 'svelte';
	import Sidebar from '../../../../../components/Sidebar.svelte';

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
    let id_usuario2: number = $derived(Number(data.id_usuario2 ?? {}));

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


<main>
    <h1>{infoAmigo.username}</h1>
    <div id="div-chat">
        <div id = "div-listaMensajes" bind:this={listaMensajes}>
            {#each mensajes as mensaje}
                <div id="mensaje">
                    <ul>
                        <li class= "li-usrname">{mensaje.username}</li>
                        <li class="li-fecha">{new Date(mensaje.fecha).toLocaleDateString('es-ES')} {new Date(mensaje.fecha).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</li>
                    </ul>
                    <p>{mensaje.contenido}</p>
                </div>
                <hr>
            {/each}
        </div>
        <input type="text" placeholder="Escribe un mensaje..." onkeydown={(e) => { if (e.key === 'Enter') enviarMensaje() }} bind:value={contenido}>
    </div>
</main>

<Sidebar
    id_usuario={id_usuario}
    canales={canales}
    amigos={amigos}
    id_usuario2={id_usuario2} 
/>

<style>
    main {
        margin-left: 250px;
    }
    #div-chat {
        margin-top: 1%;
        height: 800px;
        border-radius: 40px;
        border: 1px solid var(--border-accent);
        margin: 1% clamp(20px, 10%, 200px) 0% clamp(20px, 10%, 200px);
        background-color: var(--bg-primary);
        padding: 12px 12px;
        display: flex;
        flex-direction: column;
    }

    #div-listaMensajes {
        display: block;
        flex: 1;
        overflow-y: auto;
        border-radius: 28px 28px 0 0;
        border: none;
        background-color: var(--bg-primary);
        scrollbar-color: var(--border-accent) transparent;
        scrollbar-width: thin;
    }

    #div-listaMensajes::-webkit-scrollbar {
        width: 6px;
    }

    #div-listaMensajes::-webkit-scrollbar-track {
        background: transparent;
    }

    #div-listaMensajes::-webkit-scrollbar-thumb {
        background: var(--border-accent);
        border-radius: 10px;
    }

    #div-listaMensajes::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }

    #mensaje {
        display: block;
        margin: auto;
        margin: 1%;
        height: auto;
        border: none;
    }

    .li-usrname {
        color: #11caca;
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

    .li-fecha{
        color: var(--text-muted);
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