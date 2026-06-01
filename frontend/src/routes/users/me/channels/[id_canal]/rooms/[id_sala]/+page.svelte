<script lang="ts">
	import { tick } from 'svelte';
	import Sidebar from '../../../../../../../components/Sidebar.svelte';
	import { PUBLIC_API_URL, PUBLIC_WS_URL } from '$env/static/public';
	import { toast, Toaster } from 'svelte-sonner';
	import { notificaciones } from '../../../../../../../stores/notifications.js';
	import { browser } from '$app/environment';
    // import { beforeNavigate } from '$app/navigation';

    type Mensajes = {
        id_mensaje: number,
        contenido: string,
        username: string,
        id_usuario_emisor: number,
        fecha: Date
    };
    type Canal = {
		id_canal: number,
        nombre: string,
        rol: "participante" | "administrador"
    };
    type Amigo = {
        id_amigo: number,
        email: string,
        username: string,
        fecha_de_nacimiento: Date,
        fecha_de_alta: Date
    };
    type Sala = {
        id_sala: number,
        tipo: string,
        nombre_sala: string,
    };

    let { data } = $props();
    let mensajes: Mensajes[] = $state([]);
    let id_usuario: number = $derived(Number(data.infoUser.id_usuario ?? {}));
    let sala: Sala = $derived(data.infoSala ?? {});
    let canales: Canal[] = $derived(data.canales ?? []);
    let amigos: Amigo[] = $derived(data.amigos ?? []);
    let canal: Canal = $derived(data.canal ?? {});
    let salas: Sala[] = $derived(data.salas ?? []);

    let ws: WebSocket;
    // let cierreIntencionado = false;
    // let navegandoALogin = false;
    let listaMensajes: HTMLDivElement;

    async function scrollAbajo() {
        await tick(); // espera a que svelte actualice el DOM
        listaMensajes.scrollTop = listaMensajes.scrollHeight;
    }
    let contenido = $state("");

    // beforeNavigate (({ to }) => {
    //     if (to?.route.id === '/login' || to?.url.pathname === '/login') {
    //         navegandoALogin = true;
    //     }
    // })

    function enviarMensaje() {
        if (!contenido.trim()) return;

        // añadir localmente de forma inmediata
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
    
    $effect(() => {
        if (!browser) return;
        mensajes = data.mensajes ?? [];

         // Marcar notificaciones de esta sala como leídas
        fetch(`${PUBLIC_API_URL}/users/me/notifications/read`, {
            method: 'PATCH',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_sala: data.id_sala })
        });

        // Limpiar del store local
        notificaciones.update(n => n.filter(notif => notif.id_sala !== data.id_sala));
        // cierra el ws anterior y abre uno nuevo
        if (ws) {
            // cierreIntencionado = true;
            ws.close();
        }

        ws = new WebSocket(`${PUBLIC_WS_URL}/ws/users/me/channels/${data.id_canal}/rooms/${data.id_sala}`);
        
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
                    mensajes = mensajes.map(m => m.id_mensaje === -1 ? mensaje : m);
                } else {
                    mensajes = [...mensajes, mensaje];
                }       
                scrollAbajo();     
            }  
        };

        scrollAbajo();

        return () => ws.close(); // cleanup cuando cambia data o se destruye
    });

</script>

<main>
    <h1>{sala.nombre_sala}</h1>
    <div id="div-chat">
        <div id = "div-listaMensajes" bind:this={listaMensajes}>
            {#each mensajes as mensaje}
                <div id="mensaje">
                    <ul>
                        <li class= "li-usrname">{mensaje.username}</li>
                        <li class= "li-fecha">{new Date(mensaje.fecha).toLocaleDateString('es-ES')} {new Date(mensaje.fecha).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</li>
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
    canal={canal}
    salas={salas}
    sala={sala}
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
        /* color: #9a39ee; */
        /* color: #6111ca; */
        color: var(--accent-quaternary);
        /* color: #32eeee; */
        font-weight: bold;
        font-size: larger;
    }

    ul {
        color: var(--text-secondary);
        text-align: justify;
    }
    
    li{
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