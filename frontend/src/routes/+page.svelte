
<script lang="ts">
import {goto} from '$app/navigation';
function irARegistro() {
    goto('/sign_in')
} 

function irAIniciarSesion() {
        goto('/login')
}
</script>


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
        /* background-image: url("https://starwalk.space/gallery/images/what-is-space/1140x641.jpg"); */
        background-image: url("https://img1.wallspic.com/crops/9/0/1/8/4/148109/148109-objeto_astronomico-tierra-naturaleza-ambiente-universo-4096x3040.jpg");
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
        border: 2px solid #5865f2;
        background: #5865f2;
        color: white;
        border-radius: 6px;
        font-size: 18px;
        cursor: pointer;
    }
</style>
