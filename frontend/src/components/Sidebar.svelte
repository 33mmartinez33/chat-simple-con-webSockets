<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import DialogoBuscar from './DialogoBuscar.svelte';
	import DialogoCrearSala from './DialogoCrearSala.svelte';
	import DialogoCrearCanal from './DialogoCrearCanal.svelte';
	import BtnAdd from './BtnAdd.svelte';
	import BtnNew from './BtnNew.svelte';
	
    type Mensajes = {
        id_mensaje: number,
        contenido: string,
        username: string,
        id_usuario_emisor: number,
        fecha: Date
    };
    type Usuario = {
        id_usuario: number,
        email: string,
        username: string,
        fecha_de_nacimiento: Date,
        fecha_de_alta: Date
    };
    type Canal = {
		id_canal: number,
        nombre: string,
        rol: "PARTICIPANTE" | "ADMIN"
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

    interface Props {
        id_usuario: number;
        canales: Canal[];
        amigos: Amigo[];
        canal?: Canal;
        salas?: Sala[];
        sala?: Sala;
        id_usuario2?: number;
    }

    let {
        id_usuario,
        canales = [],
        amigos = [],
        canal = undefined,
        salas = [],
        sala = undefined,
        id_usuario2 = undefined,
    } = $props();


    let dialogoCrearCanal = $state<any>(null);
    let dialogoCrearSala = $state<any>(null);
    let dialogoCanal = $state<any>(null);
    let dialogoAmigo = $state<any>(null);

    const esAdmin = $derived(canal?.rol?.toLowerCase() === 'administrador');
    const rol = $derived(esAdmin ? "Adm": "Std");

    function irCanal(id_canal : number){
        goto (`/usuarios/${id_usuario}/canales/${id_canal}`);
    }
    function irSala(id_canal: number, id_sala: number){
        goto (`/usuarios/${id_usuario}/canales/${id_canal}/salas/${id_sala}`);
    }
    function irAmigo(id_usuario2: number){
        goto (`/usuarios/${id_usuario}/amigos/${id_usuario2}`);
    }

</script>


<aside class="sidebar">
    <ul>
        <li>
            <div class="div-header">
                <p class="p-sidebar">Canales</p>
                <div id="div-botones">
                <BtnAdd onclick={() => dialogoCanal?.abrir()} title= "Añadir canal"/>
                <BtnNew onclick={() => dialogoCrearCanal?.abrir()} title="Crear canal" />
                </div>
            </div> 
        </li>
        <li>
            <ul class="ul-sidebar">                                
                {#each canales as canalSec}
                    {#if (canalSec.id_canal == canal?.id_canal)}
                        <li>
                            <div class="div-header-canal">
                                <p class = "p-resaltado">{canal?.nombre} - <span>{rol}</span></p>
                                {#if esAdmin}
                                    <BtnNew onclick={() => dialogoCrearSala?.abrir()} title="Crear sala"/>
                                {/if}
                            </div>
                            {#each salas as s}
                            <ul>
                                {#if s.id_sala == sala?.id_sala}
                                    <li class="li-sala-resaltado">
                                        <button class="btn-sidebar" onclick={() => {irSala(canal!.id_canal, s.id_sala)}}>{s.nombre_sala}</button>
                                    </li>
                                {:else}
                                    <li class="li-salas">
                                        <button class="btn-sidebar" onclick={() => {irSala(canal!.id_canal, s.id_sala)}}>{s.nombre_sala}</button>
                                    </li>
                                {/if}
                            </ul>
                            {/each}
                        </li>
                    {:else}                             
                        <li>
                            <button class="btn-sidebar" onclick={() => {irCanal(canalSec.id_canal)}}>{canalSec.nombre}</button>
                        </li>
                    {/if}
                {/each}
            </ul>
        </li>
    </ul>
    <ul>
        <li>
            <div class="div-header">
                <p class = "p-sidebar">Amigos</p>
                <BtnAdd onclick={() => dialogoAmigo?.abrir()} title= "Añadir amigo"/>
            </div>
            <ul>
                {#each amigos as amigo}
                    {#if amigo.id_amigo == id_usuario2}
                    <li class="li-amigo-res">
                        <button  class="btn-sidebar" onclick={() => {irAmigo(amigo.id_amigo)}}>{amigo.username}</button>
                    </li> 
                    {:else}
                    <li class="li-amigo-no-res">
                        <button  class="btn-sidebar" onclick={() => {irAmigo(amigo.id_amigo)}}>{amigo.username}</button>
                    </li> 
                    {/if}   
                {/each}
            </ul>
        </li>        
    </ul>

</aside>



<DialogoCrearCanal 
    bind:ref = {dialogoCrearCanal}
    id_usuario = {Number(id_usuario)}
    onclose = {invalidateAll}
/>

<DialogoCrearSala
    bind:ref = {dialogoCrearSala}
    id_usuario = {Number(id_usuario)}
    id_canal = {canal?.id_canal}
    onclose = {invalidateAll}
/>
<DialogoBuscar
    bind:ref={dialogoCanal}
    titulo="Añadir canal"
    endpoint="http://localhost:8001/canales"
    labelNombre="nombre"
    onclose={invalidateAll}
    onAnhadir={async (item) => {
        await fetch(`http://localhost:8001/usuarios/${id_usuario}/canales/${item.id_canal}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_canal: item.id_canal })
        });
    }}
/>
<DialogoBuscar
    bind:ref={dialogoAmigo}
    titulo="Añadir amigo"
    endpoint="http://localhost:8001/usuarios"
    labelNombre="username"
    onclose={invalidateAll}
    onAnhadir={async (item) => {
        await fetch(`http://localhost:8001/usuarios/${id_usuario}/amigos/${item.id_usuario}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_usuario: item.id_usuario })
        });
    }}
/>

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
        width: auto;
        padding: 4px 8px;
        background: none;
        border: none;
        line-height: 1.5;
    }

    .p-resaltado {
        font-weight: bold;
        color: var(--accent-tertiary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;          
        min-width: 0;
        margin-left: 8px;
    }

    .li-amigo-res {
        font-weight: bold;
        color: var(--accent-tertiary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;          
        min-width: 0;
        margin-left: 0px;
    }

    span {
        font-size: smaller;
        /* color */
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

    .div-header-canal{
        display: flex;
        align-items: center;
        justify-content: space-evenly;
        width: 100%;
        gap: 0.25rem;
        height: 32px;
    }

    .li-salas{
        margin-left: 1rem;
    }

    .li-sala-resaltado{
        color: var(--accent-tertiary);
        margin-left: 1rem;
        font-weight: bold;
    }

    #div-botones{
        display: flex;
        gap: 0.25rem;
        margin-left: auto;
    }
</style>