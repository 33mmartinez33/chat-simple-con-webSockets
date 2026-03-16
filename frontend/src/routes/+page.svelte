
<script>
function irARegistro() {
    // añadir logica para el push.navigator
} 

function irAIniciarSesion() {
    // añadir lógica
}
</script>


<main>
    <h1>NEXUS</h1>
    <p>Conecta. Chatea. Crea.</p>
    <div>
        <button onclick={irAIniciarSesion}>Iniciar sesión</button>
        
        <button onclick={irARegistro}>Registrarse</button>
    </div>
</main>

<!-- Falta añadir tamaños variables segun ventana etc -->
<style>
    h1,p{
        text-align: center;
    }
    h1{
        margin-top: 300px;
        font-size: 60px;
        font-weight: bold;
    }
    p{
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
