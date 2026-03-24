<script lang="ts">
	import { invalidateAll } from '$app/navigation';
    import DialogoBuscar from '../../../../../components/DialogoBuscar.svelte';
	import DialogoCrearSala from '../../../../../components/DialogoCrearSala.svelte';
    import BtnNew from '../../../../../components/BtnNew.svelte';
	import DialogoCrearCanal from '../../../../../components/DialogoCrearCanal.svelte';

    type Canal = {
        id_canal: number;
        nombre: string;
        contenido_principal: string;
        rol: "PARTICIPANTE" | "ADMIN";
    };

    type Sala = {
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

    let dialogoCrearCanal = $state<any>(null);
    let dialogoCrearSala = $state<any>(null);
    let dialogoCanal = $state<any>(null);
    let dialogoAmigo = $state<any>(null);

    const esAdmin = $derived(canal.rol?.toLowerCase() === 'administrador');
    
    const rol = $derived(esAdmin ? "Adm": "Std");

</script>


<aside class="sidebar">
    <ul>
        <li>
            <div class="div-header">
                <p class="p-sidebar">Canales</p>
                <BtnNew onclick={() => dialogoCrearCanal?.abrir()} title="Crear canal" />
            </div>         
        </li>
        <li>
            <ul class="ul-sidebar">
                <li>
                    <div class="div-header">
                        <p id = "p-Canal">{canal.nombre} - <span>{rol}</span></p>
                        {#if esAdmin}
                                <BtnNew onclick={() => dialogoCrearSala?.abrir()} title="Crear sala"/>
                        {/if}
                    </div>
                    <ul>
                        {#each salas as sala}
                            <li id="li-salas">
                                <button class="btn-sidebar">{sala.nombre_sala}</button>
                            </li>
                        {/each}
                    </ul>
                </li>
                    {#each canales as canalSec}
                        {#if (canalSec.nombre != canal.nombre)}
                            <li id="p-canales-no-ppal">
                                <button class="btn-sidebar">{canalSec.nombre}</button>
                            </li>
                        {/if}
                    {/each}
            </ul>
        </li>
        <li>
            <p class = "p-sidebar">Amigos</p>
            <ul>
                {#each amigos as amigo}
                    <li class="li-sidebar">
                        <button  class="btn-sidebar" >{amigo.username}</button>
                    </li>    
                {/each}
            </ul>
        </li>        
    </ul>

</aside>

<main>
    <h1>{canal.nombre}</h1>
    <div class="contenido-principal">
    Post principal de bienvenida <br>
        {canal.contenido_principal}
    </div>
</main>
<DialogoCrearCanal 
    bind:ref = {dialogoCrearCanal}
    id_usuario = {Number(data.id_usuario)}
    onclose = {invalidateAll}
/>

<DialogoCrearSala
    bind:ref = {dialogoCrearSala}
    id_usuario = {Number(data.id_usuario)}
    id_canal = {canal.id_canal}
    onclose = {invalidateAll}
/>
<DialogoBuscar
    bind:ref={dialogoCanal}
    titulo="Añadir canal"
    endpoint="http://localhost:8001/canales"
    labelNombre="nombre"
    onclose={invalidateAll}
    onAnhadir={async (item) => {
        await fetch(`http://localhost:8001/usuarios/${data.id_usuario}/canales/${item.id_canal}`, {
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
        await fetch(`http://localhost:8001/usuarios/${data.id_usuario}/amigos/${item.id_usuario}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_usuario: item.id_usuario })
        });
    }}
/>

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
        padding-top: 100px;
        text-align: left;
    }

.p-sidebar {
    /* margin-bottom: 12px !important; */
    color: var(--accent-secondary);
    font-weight: bold;
    font-size: 20px;
    
    /* ← FUERZA alineación exacta */
    display: flex !important;
    align-items: center !important;
    line-height: 24px !important;     /* Ajusta al centro del BtnAdd 26px */
    height: 26px !important;
    margin-top: 0 !important;
}

    .li-sidebar {
        display: flex;
        flex-direction: column;
        text-align: left;
        width: fit-content;
    }

    .ul-sidebar {
        display: flex;
        flex-direction: column;
    }

    .btn-sidebar {
        text-align: left;
        cursor: pointer;
        width: auto;
        color: var(--text-secondary);
        padding: 4px 8px;
        background: none;
        border: none;
        line-height: 1.5;
    }

    #p-Canal {
        font-size: 20px;
        font-weight: bold;
        color: var(--accent-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;          
        min-width: 0; 
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
        margin-bottom: 10px;
        margin-top: 5px;
        gap: 0.25rem;
    }

    .contenido-principal {
        margin-top: 10%;
    }

    #li-salas{
        margin-left: 2rem;
    }
    
</style>