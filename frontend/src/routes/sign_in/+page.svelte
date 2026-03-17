<script>
    function registrarse() {
        // Lógica
    }
</script>

<main>
    <h1>¡Únete a Nexus!</h1>
    <div>
        <label for="email">Email</label>
        <input type="email" id="email">
        
        <label for="username">Nombre de usuario</label>
        <input type="text" id= "username">

        <label for="password">Contraseña</label>
        <input type="password" id = "password">

        <label for="birthdate">Fecha de nacimiento</label>
        <input type="date" id = "birthdate">

        <button class="botonFormulario" onclick={registrarse}>Registrarse</button>
    </div>
</main>

<style>

    h1{
        margin-top: 110px;
    }
    div{
        margin-top: 40px;
        width: 280px;
        margin-left: auto;
        margin-right: auto;
    }
/* Invierte el color del icono del calendario de negro a blanco*/
    input[type="date"]::-webkit-calendar-picker-indicator {
    filter: invert(1);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    }
</style>