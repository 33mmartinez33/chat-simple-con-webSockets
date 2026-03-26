
<script lang="ts">
import {goto} from '$app/navigation';
function irARegistro() {
    goto('/sign_in')
} 

function irAIniciarSesion() {
        goto('/login')
}
</script>

<svelte:head>
  <link rel="preload" href="/assets/img/fondo_principal (1).webp" as="image" fetchpriority="high">
</svelte:head>

<main>
    <div id= "fondo">
        <div>
            <h1>NEXUS</h1>
            <h2>Conecta. Chatea. Crea.</h2>
            <div>
                <button onclick={irAIniciarSesion}>Iniciar sesión</button>        
                <button onclick={irARegistro}>Registrarse</button>
            </div>
        </div>

    </div>
</main>

<!-- Falta añadir tamaños variables segun ventana etc -->
<style>
    #fondo{
        height: 100vh;
        background-image: url("assets/img/fondo_principal (1).webp");
        background-size: cover;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    h1,h2{
        text-align: center;
    }
    div{
        display: block;
    }
    h1{
        /* margin-top: 300px; */
        /* padding-top: 300px; */
        font-size: 60px;
        font-weight: bold;
    }
    h2{
        font-size: 32px;
    }
    button {
        width: 160px;
        margin: 0 5px;
        margin-top: 20px;
        padding: 12px 24px;     
        border: 2px solid var(--border-accent);
        background: var(--bg-secondary);
        color: var(--text-primary);
        border-radius: 6px;
        font-size: 18px;
        cursor: pointer;
    }
    button:hover {
        background: color-mix(in srgb, var(--bg-primary) 90%, var(--accent-primary));
        transform: scale(1.05);
        transition: all 0.1s;
    }
</style>
