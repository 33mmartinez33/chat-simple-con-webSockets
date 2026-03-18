<script lang="ts">
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
    let { data } = $props();
    let canales: Canal[] = $derived(data.canales ?? []); // ?? es un operador nullish coalescing, si el de la izq es null devuelve el de la derecha
    let amigos: Amigo[] = $derived(data.amigos ?? []);
    let id_usuario = $derived(data.id_usuario); //derived innecesario, el id_usuario no cambiará

// TODO agregar boton para añadir amigos y añadir canales etc
    function irCanal(id_canal : number){
        window.location.href = `/usuarios/${id_usuario}/canales/${id_canal}`;
    }
    function irAmigo(id_usuario2: number){
        window.location.href = `/usuarios/${id_usuario}/amigos/${id_usuario2}`;
    }

</script>


<!-- TODO crear un canal, añadir canales (ver lista de canales disponibles a seguir), añadir amigo (introducir username y bbdd busca) -->
<!-- TODO añadir cargando para que no se renderice antes de tiempo el no tienes amigos/canales -->
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
            <h2>Canales</h2>
            {#if canales.length === 0}
                <div class= "item">No sigues ningún canal</div>
            {:else}
                {#each canales as canal}
                    <div class="item">
                        <button onclick={() => irCanal(canal.id_canal)}>{canal.nombre}</button>
                    </div>
                {/each}

            {/if}            
                <div class= "finColumna"></div>
        </div>

        <!-- AMIGOS -->
        <div class="columna">
            <h2>Amigos</h2>
            {#if amigos.length != 0}
                {#each amigos as amigo}
                    <!-- <div class="item">{amigo.username}</div> -->
                    <div class="item">
                        <button onclick={() => {irAmigo(amigo.id_amigo)}}>{amigo.username}</button>
                    </div>
                {/each}
            {:else}
                <div class= "item">No sigues a ningún amigo</div>
            {/if}            
                <div class= "finColumna"></div>
        </div>
    </div>
</main>

<style>
    h2{
        font-size: 24px;
        padding: 4px;
    }
    #texto {
        margin-top: 120px
    }
    .columnas {
        margin: auto;
        margin-top: 80px;
        width: 800px;
        display: flex;
        gap: 2rem;
        min-height: 300px;
    }
    .columna {
        flex: 1;
        background-color: #5865f2;
        border-radius: 12px;
    }
    .item {
        background-color: whitesmoke;
        color: black;
    }
    button{
        cursor: pointer;
        margin-left: auto;
        margin-right: auto;
        padding:1px 12px;
    }
    .finColumna {
        flex: 1;
        background-color: #5865f2;
        border-radius: 12px;
        min-height: 22px;
    }
</style>