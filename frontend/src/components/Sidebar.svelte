<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import DialogoBuscar from './DialogoBuscar.svelte';
	import DialogoCrearSala from './DialogoCrearSala.svelte';
	import DialogoCrearCanal from './DialogoCrearCanal.svelte';
	import BtnAdd from './BtnAdd.svelte';
	import BtnNew from './BtnNew.svelte';
	import { PUBLIC_API_URL } from '$env/static/public';
    import { onMount } from 'svelte';
	import { notificaciones } from '../stores/notifications';

    type Canal = {
		id_canal: number,
        nombre: string,
        rol?: "participante" | "administrador"
    };
    type Amigo = {
        id_amigo: number,
        email: string,
        username: string,
        fecha_de_nacimiento?: Date,
        fecha_de_alta?: Date
    };
    type Sala = {
        id_sala: number,
        tipo: string,
        nombre_sala: string,
    };

    interface Props {
        canales: Canal[];
        amigos: Amigo[];
        canal?: Canal;
        salas?: Sala[];
        sala?: Sala;
        id_usuario2?: number;
    }

    let {
        canales = [],
        amigos = [],
        canal = undefined,
        salas = [],
        sala = undefined,
        id_usuario2 = undefined,
    }: Props = $props();

    let dialogoCrearCanal = $state<any>(null);
    let dialogoCrearSala = $state<any>(null);
    let dialogoCanal = $state<any>(null);
    let dialogoAmigo = $state<any>(null);
    let mounted = $state(false);

    const notifPorSala = $derived(
        Object.fromEntries(
            ($notificaciones)
                .filter(n => n.tipo === 'sala')
                .reduce((acc, n) => {
                    acc.set(n.id_sala!, (acc.get(n.id_sala!) ?? 0) + 1);
                    return acc;
                }, new Map<number, number>())
        )
    );

    const notifPorAmigo = $derived(
        Object.fromEntries(
            ($notificaciones)
                .filter(n => n.tipo === 'dm')
                .reduce((acc, n) => {
                    acc.set(n.id_usuario_emisor!, (acc.get(n.id_usuario_emisor!) ?? 0) + 1);
                    return acc;
                }, new Map<number, number>())
        )
    );

    onMount(() => {
        mounted = true;
    });

    const esAdmin = $derived(canal?.rol?.toLowerCase() === 'administrador');
    const rol = $derived(esAdmin ? "Adm": "Std");

    function irCanal(id_canal: number){
        goto(`/users/me/channels/${id_canal}`);
    }
    function irSala(id_canal: number, id_sala: number){
        goto(`/users/me/channels/${id_canal}/rooms/${id_sala}`);
    }
    function irAmigo(id_usuario2: number){
        goto(`/users/me/friends/${id_usuario2}`);
    }
</script>


<aside class="sidebar">
    <ul>
        <li>
            <div class="div-header">
                <p class="p-sidebar">Canales</p>
                <div id="div-botones">
                    <BtnAdd onclick={() => dialogoCanal?.abrir()} title="Añadir canal"/>
                    <BtnNew onclick={() => dialogoCrearCanal?.abrir()} title="Crear canal" />
                </div>
            </div> 
        </li>
        <li>
            <ul class="ul-sidebar">                                
                {#if canales.length === 0}
                    <li class="li-empty">
                        Usa 🔍 para unirte o <strong>+</strong> para crear uno
                    </li>
                {/if}
                {#each canales as canalSec}
                    {#if (canalSec.id_canal == canal?.id_canal)}
                        <li class:li-canal-activo={!sala?.id_sala}>
                            <div class="div-header-canal">
                                <button class="btn-sidebar" onclick={() => irCanal(canal!.id_canal)}>
                                    {canal?.nombre} <span>{rol}</span>
                                </button>
                                {#if esAdmin}
                                    <BtnNew onclick={() => dialogoCrearSala?.abrir()} title="Crear sala"/>
                                {/if}
                            </div>
                            {#each salas as s}
                                <ul>
                                    {#if s.id_sala == sala?.id_sala}
                                        <li class="li-sala-resaltado">
                                            <button class="btn-sidebar" onclick={() => irSala(canal!.id_canal, s.id_sala)}>
                                                {s.nombre_sala}
                                                {#if notifPorSala[s.id_sala]}
                                                    <span class="badge">{notifPorSala[s.id_sala]}</span>
                                                {/if}
                                            </button>
                                        </li>
                                    {:else}
                                        <li class="li-salas">
                                            <button class="btn-sidebar" onclick={() => irSala(canal!.id_canal, s.id_sala)}>
                                                {s.nombre_sala}
                                                {#if notifPorSala[s.id_sala]}
                                                    <span class="badge">{notifPorSala[s.id_sala]}</span>
                                                {/if}
                                            </button>
                                        </li>
                                    {/if}
                                </ul>
                            {/each}
                        </li>
                    {:else}                             
                        <li>
                            <button class="btn-sidebar" onclick={() => irCanal(canalSec.id_canal)}>{canalSec.nombre}</button>
                        </li>
                    {/if}
                {/each}
            </ul>
        </li>
    </ul>
    <ul>
        <li>
            <div class="div-header">
                <p class="p-sidebar">Amigos</p>
                <BtnAdd onclick={() => dialogoAmigo?.abrir()} title="Añadir amigo"/>
            </div>
            <ul>
                {#if amigos.length === 0}
                    <li class="li-empty">
                        Usa 🔍 para añadir un amigo
                    </li>
                {/if}
                {#each amigos as amigo}
                    {#if amigo.id_amigo == id_usuario2}
                        <li class="li-amigo-res">
                            <button class="btn-sidebar" onclick={() => irAmigo(amigo.id_amigo)}>
                                {amigo.username}
                                {#if notifPorAmigo[amigo.id_amigo]}
                                    <span class="badge">{notifPorAmigo[amigo.id_amigo]}</span>
                                {/if}
                            </button>
                        </li> 
                    {:else}
                        <li class="li-amigo-no-res">
                            <button class="btn-sidebar" onclick={() => irAmigo(amigo.id_amigo)}>
                                {amigo.username}
                                {#if notifPorAmigo[amigo.id_amigo]}
                                    <span class="badge">{notifPorAmigo[amigo.id_amigo]}</span>
                                {/if}
                            </button>
                        </li> 
                    {/if}   
                {/each}
            </ul>
        </li>        
    </ul>
</aside>

{#if mounted}
    <DialogoCrearCanal 
        bind:ref={dialogoCrearCanal}
        onclose={invalidateAll}
    />
    <DialogoBuscar
        bind:ref={dialogoCanal}
        titulo="Añadir canal"
        endpoint={`${PUBLIC_API_URL}/channels`}
        labelNombre="nombre"
        onclose={invalidateAll}
        onAnhadir={async (item) => {
            await fetch(`${PUBLIC_API_URL}/users/me/channels/${item.id_canal}`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_canal: item.id_canal })
            });
        }}
    />
    <DialogoBuscar
        bind:ref={dialogoAmigo}
        titulo="Añadir amigo"
        endpoint={`${PUBLIC_API_URL}/users`}
        labelNombre="username"
        onclose={invalidateAll}
        onAnhadir={async (item) => {
            await fetch(`${PUBLIC_API_URL}/users/me/friends/${item.id_usuario}`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_usuario: item.id_usuario })
            });
        }}
    />
    {#if esAdmin}
        <DialogoCrearSala
            bind:ref={dialogoCrearSala}
            id_canal={canal!.id_canal}
            onclose={invalidateAll}
        />
    {/if}
{/if}

<style>
    ul {
        color: var(--text-secondary);
        text-align: justify;
    }

    p {
        text-align: justify;
    }

    aside {
        width: 250px;
        flex-shrink: 0;
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        background: var(--bg-secondary);
        padding: 1rem;
        padding-top: 100px;
        text-align: left;
    }

    .p-sidebar {
        color: var(--accent-secondary);
        font-weight: bold;
        font-size: 20px;
    }

    .ul-sidebar {
        display: flex;
        flex-direction: column;
    }

    .btn-sidebar {
        text-align: left;
        cursor: pointer;
        width: 100%;
        padding: 6px 10px;
        background: none;
        border: none;
        border-radius: 6px;
        line-height: 1.5;
        display: flex;
        align-items: center;
        gap: 4px;
        color: var(--text-secondary);
        transition: background 0.15s, color 0.15s;
    }

    .btn-sidebar:hover {
        background: color-mix(in srgb, var(--bg-secondary) 75%, var(--accent-tertiary));
        color: var(--text-primary);
    }

    .li-canal-activo .div-header-canal .btn-sidebar {
        color: var(--accent-tertiary);
        font-weight: bold;
        background: color-mix(in srgb, var(--bg-secondary) 65%, var(--accent-tertiary));
        flex: 1;
    }

    .li-canal-activo .div-header-canal .btn-sidebar:hover {
        background: color-mix(in srgb, var(--bg-secondary) 55%, var(--accent-tertiary));
    }

    .li-amigo-res {
        overflow: hidden;
        min-width: 0;
    }

    .li-amigo-res .btn-sidebar {
        color: var(--accent-tertiary);
        font-weight: bold;
        background: color-mix(in srgb, var(--bg-secondary) 65%, var(--accent-tertiary));
    }

    .li-amigo-res .btn-sidebar:hover {
        background: color-mix(in srgb, var(--bg-secondary) 55%, var(--accent-tertiary));
    }

    .li-empty {
        font-size: 0.75rem;
        color: var(--text-secondary, #888);
        padding: 4px 8px;
        font-style: italic;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: color-mix(in srgb, var(--accent-tertiary) 50%, transparent);
        color: var(--text-primary);
        border-radius: 50%;
        width: 18px;
        height: 18px;
        font-size: 11px;
        font-weight: bold;
        margin-left: 4px;
        flex-shrink: 0;
    }

    span {
        font-size: smaller;
    }

    .div-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        height: 2rem;
        line-height: 2rem;  
        margin-top: 5px;
        gap: 0.25rem;
    }

    .div-header-canal {
        display: flex;
        align-items: center;
        justify-content: space-evenly;
        width: 100%;
        gap: 0.25rem;
        height: 32px;
    }

    .li-salas {
        margin-left: 1rem;
    }

    .li-sala-resaltado {
        margin-left: 1rem;
    }

    .li-sala-resaltado .btn-sidebar {
        color: var(--accent-tertiary);
        font-weight: bold;
        background: color-mix(in srgb, var(--bg-secondary) 65%, var(--accent-tertiary));
    }

    .li-sala-resaltado .btn-sidebar:hover {
        background: color-mix(in srgb, var(--bg-secondary) 55%, var(--accent-tertiary));
    }

    #div-botones {
        display: flex;
        gap: 0.25rem;
        margin-left: auto;
    }
</style>