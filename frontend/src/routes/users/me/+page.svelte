<script lang="ts">
import { goto, invalidateAll } from '$app/navigation';
import DialogoBuscar from '../../../components/DialogoBuscar.svelte';

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

    // type InfoUser = {
    //     id_usuario: number;
    //     email: string;
    //     username: string;
    //     fecha_de_nacimiento: Date;
    //     fecha_de_alta: Date;
    // }

    let { data } = $props();
    let canales: Canal[] = $derived(data.canales ?? []);
    let amigos: Amigo[] = $derived(data.amigos ?? []);
    // let infoUser: InfoUser = $derived(data.infoUser);
    // let id_usuario = $derived(Number(infoUser.id_usuario));

    let dialogoCanal = $state<any>(null);
    let dialogoAmigo = $state<any>(null);

    function irCanal(id_canal: number) {
        goto(`/users/me/channels/${id_canal}`);
    }
    
    function irAmigo(id_usuario2: number) {
        goto(`/users/me/friends/${id_usuario2}`);
    }

</script>


<!-- TODO crear un canal -->
<main>
    <div id="texto"> 
        <h1>Bienvenido usuario</h1>
        <p>Aquí podras ver la lista de canales que sigues, así como una lista de tus amigos</p>
        <p>Dentro de cada canal hay salas, en las cuales podras interactuar con otros usuarios</p>
        <p>También puedes interactuar directamente con tus amigos</p>
    </div>
        <div class="columnas">
        
        <!-- CANALES -->
        <div class="columna">
            <div class="headerColumna">
                <h2>Canales</h2>
                <button class="botonAñadir" onclick={() => dialogoCanal?.abrir()}>+</button>
            </div>
            {#if canales.length === 0}
                <div class= "item">No sigues ningún canal</div>
            {:else}
                <div class= "scroll">
                {#each canales as canal}
                    <div class="item">
                        <button onclick={() => irCanal(canal.id_canal)}>{canal.nombre}</button>
                    </div>
                {/each}
                </div>
            {/if}            
                <div class= "finColumna"></div>
        </div>

        <!-- AMIGOS -->
        <div class="columna">
            <div class="headerColumna">
                <h2>Amigos</h2>
                <button class="botonAñadir" onclick={() => dialogoAmigo?.abrir()}>+</button>
            </div>
            {#if amigos.length != 0}
                <div class="scroll">
                {#each amigos as amigo}
                    <div class="item">
                        <button onclick={() => {irAmigo(amigo.id_amigo)}}>{amigo.username}</button>
                    </div>
                {/each}
                </div>
            {:else}
                <div class= "item">No sigues a ningún amigo</div>
            {/if}            
                <div class= "finColumna"></div>
        </div>
    </div>
</main>

<DialogoBuscar
    bind:ref={dialogoCanal}
    titulo="Añadir canal"
    endpoint="http://localhost:8001/channels"
    labelNombre="nombre"
    onclose={invalidateAll}
    onAnhadir={async (item) => {
        await fetch(`http://localhost:8001/users/me/channels/${item.id_canal}`, {
            method: 'POST',
            credentials: "include",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_canal: item.id_canal })
        });
    }}
/>
<DialogoBuscar
    bind:ref={dialogoAmigo}
    titulo="Añadir amigo"
    endpoint="http://localhost:8001/users"
    labelNombre="username"
    onclose={invalidateAll}
    onAnhadir={async (item) => {
        await fetch(`http://localhost:8001/users/me/friends/${item.id_usuario}`, {
            method: 'POST',
            credentials: "include",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_usuario: item.id_usuario })
        });
    }}
/>

<style>
    h2 {
        font-size: 24px;
        padding: 4px;
        flex: 1;
        text-align: left;
        color: var(--text-primary);
        margin-left: 10px;
    }
    
    #texto {
        margin-top: 120px;
        color: var(--text-primary);
    }
    
    .columnas {
        margin: auto;
        margin-top: 80px;
        width: 800px;
        display: flex;
        gap: 2rem;
        min-height: 300px;
        max-height: 300px;
    }
    
    .columna {
        flex: 1;
        background-color: var(--bg-elevated);
        border-radius: 12px;
        border: solid var(--border-accent) 1px;
        text-align: left;
    }
    
    .scroll {
        max-height: 238px;
        overflow-y: auto;
        flex: 1;
        flex-direction: column;
        gap: 6px;
        padding: 0 1%;
    } 
    
    .item {
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
        margin-top: 2px;
        margin-bottom: 2px;
        border-radius: 10px;
        height: 40px;
        display: flex;
        /* align-items: left; */
        justify-content: center;
    }
    
    button {
        cursor: pointer;
        margin-left: auto;
        margin-right: auto;
        padding: 1px 12px;
        width: 180px;
        font-size: 18px;
        background: var(--bg-input);
        color: var(--text-primary);
        border: 1px solid var(--border-menu);
        border-radius: 8px;
        text-align: left;
    }
    
    .finColumna {
        flex: 1;
        background-color: var(--bg-aside);
        border-radius: 12px;
        min-height: 22px;
    }
    
    .botonAñadir {
        position: absolute;
        right: 0.5rem;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: none;
        background: var(--btn-primary);
        color: var(--text-primary);
        font-size: 1.5rem;
        display: flex;
        justify-content: center;
        line-height: 1;
    }
    
    .headerColumna {
        display: flex;
        align-items: center;
        position: relative;
    }

    /* Scrollbar */
    .scroll::-webkit-scrollbar {
        width: 6px;
    }
    .scroll::-webkit-scrollbar-track {
        background: transparent;
    }
    .scroll::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    .scroll::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    .scroll {
        scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
        scrollbar-width: thin;
    }
</style>