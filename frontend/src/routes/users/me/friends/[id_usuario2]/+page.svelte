<script lang="ts">
    import { tick } from 'svelte';
	import Sidebar from '../../../../../components/Sidebar.svelte';
    import { PUBLIC_API_URL, PUBLIC_WS_URL } from "$env/static/public";
	import { toast, Toaster } from 'svelte-sonner';
	import { notificaciones } from '../../../../../stores/notifications.js';
	import { browser } from '$app/environment';
    // import { beforeNavigate } from '$app/navigation';

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
		id_canal: number
        nombre: string
        rol: "participante" | "administrador"
    }

    type InfoUser = {
        id_usuario: number;
        email: string;
        username: string;
        fecha_de_nacimiento: Date;
        fecha_de_alta: Date;
    }

    let { data } = $props();
    let mensajes: Mensajes[] = $state([]);
    let infoAmigo : Amigo = $derived(data.infoAmigo ?? {});
    let canales: Canal[] = $derived(data.canales ?? []);
    let amigos: Amigo[] = $derived(data.amigos ?? []);
    let infoUser: InfoUser = $derived(data.infoUser ?? {});
    let id_usuario: number = $derived(Number(infoUser.id_usuario ?? {}));
    let id_usuario2: number = $derived(Number(data.id_usuario2 ?? {}));
    let contenido = $state("");

    let ws: WebSocket;
    // let cierreIntencionado = false;
    // let navegandoALogin = false
    let listaMensajes: HTMLDivElement;

    // beforeNavigate (({ to }) => {
    //     if (to?.route.id === '/login' || to?.url.pathname === '/login') {
    //         navegandoALogin = true;
    //     }
    // })

    // Espera a que Svelte actualice el DOM y luego hace scroll hasta el último mensaje
    async function scrollAbajo() {
        await tick();
        listaMensajes.scrollTop = listaMensajes.scrollHeight;
    }

    // Envía el mensaje por WebSocket y lo añade localmente con id_mensaje = -1
    // El id definitivo llega por el evento onmessage y reemplaza la entrada temporal
    function enviarMensaje() {
        if (!contenido.trim()) return;

        // Añadir localmente de forma inmediata para que la UI sea instantánea
        mensajes = [...mensajes, {
            id_mensaje: -1,
            contenido,
            username: data.infoUser.username,
            id_usuario_emisor: id_usuario,
            fecha: new Date()
        }];

        ws.send(JSON.stringify({ contenido }));
        contenido = '';
        scrollAbajo();
    }

    // Efecto reactivo: se ejecuta al abrir el DM o cuando cambia el amigo seleccionado
    // Abre un nuevo WebSocket, marca las notificaciones como leídas y carga los mensajes
    $effect(() => {
        if (!browser) return;
        mensajes = data.mensajes ?? [];
        infoAmigo = data.infoAmigo ?? {};

        // Marcar notificaciones de este DM como leídas en el servidor
        fetch(`${PUBLIC_API_URL}/users/me/notifications/read`, {
            method: 'PATCH',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_usuario_emisor: data.id_usuario2 })
        });

        // Limpiar del store local para que el badge desaparezca de inmediato
        notificaciones.update(n => n.filter(notif => notif.id_usuario_emisor !== data.id_usuario2));

        // Cierra el WebSocket anterior antes de abrir uno nuevo (cambio de amigo)
        if (ws) {
            ws.close();
        }

        ws = new WebSocket(`${PUBLIC_WS_URL}/ws/users/me/friends/${data.id_usuario2}`);

        ws.onerror = () => {
            toast.error('Error de conexión');
        };

        // ws.onclose = (event) => {
        //     if (event.code !== 1000 && !cierreIntencionado) {
        //         toast.error('Conexión perdida', {
        //             action: {
        //                 label: 'Reconectar',
        //                 onClick: () => window.location.reload()
        //             }
        //         });
        //     }
        // };

        ws.onmessage = (event) => {
            const mensaje = JSON.parse(event.data);
            if (mensaje.error) {
                toast.error(mensaje.error);
            } else {
                if (mensaje.id_usuario_emisor === id_usuario) {
                    // Reemplaza el mensaje temporal (id = -1) con el confirmado por el servidor
                    mensajes = mensajes.map(m => m.id_mensaje === -1 ? mensaje : m);
                } else {
                    mensajes = [...mensajes, mensaje];
                }
                scrollAbajo();
            }
        };

        scrollAbajo();

        return () => ws.close(); // Cleanup al cambiar de amigo o desmontar el componente
    });

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
<Toaster/>

<Sidebar
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
        color: var(--accent-quaternary);
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
        background-color: var(--bg-secondary);
    }
</style>