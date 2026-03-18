<script>
    let username = "";
    let contraseña = "";
    // const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'; // Se va a usar loacalhost porque aun no tengo .env

    async function login() {
        const response = await fetch('http://localhost:8001/login', { //consulta el endpoint con esta ruta 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // ← JSON es lo que espera el backend
            },
            body: JSON.stringify({
                username: username,
                contrasenha: contraseña
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.token);
            localStorage.setItem('id_usuario', data.id_usuario.toString());
            window.location.href = `/usuarios/${data.id_usuario}`; // Redirige
        } else { 
            const error = await response.json();
            alert(error.detail);
        }
    }
</script>

<main>
    <h1>¡Bienvenido!</h1>
    <div>
        <form onsubmit={(e) => { e.preventDefault(); login(); }}>
            <label for="username" id="primerLabel">Nombre de usuario</label>
            <input type="text" id="username" bind:value={username}>

            <label for="contraseña">Contraseña</label>
            <input type="password" id="contraseña" bind:value={contraseña}>

            <button class="botonFormulario" type="submit">Iniciar Sesión</button>
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