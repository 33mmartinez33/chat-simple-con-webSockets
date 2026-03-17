<script>
    function login() {
        // logica
    }
</script>

<main>
    <h1>¡Bienvenido!</h1>
    <div>
        <form action="">
            <label for="username" id="primerLabel">Nombre de usuario</label>
            <input type="text" id="username">

            <label for="contraseña">Contraseña</label>
            <input type="password" id="contraseña">

            <button class="botonFormulario" onclick={login}>Iniciar Sesión</button>
        </form>
    </div>
</main>

<style>
    h1{
        font-size: 60px;
        margin-top: 170px;
    }
    div{
        margin-top: 40px;
        width: 280px;
        margin-left: auto;
        margin-right: auto;
    }
</style>