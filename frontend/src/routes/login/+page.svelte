<script>
    let username = "";
    let contraseña = "";

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
    <div class="div-ext">
        <h1>¡Bienvenido!</h1>
        <div class="div-form">
            <form onsubmit={(e) => { e.preventDefault(); login(); }}>
                <label for="username" id="primerLabel">Nombre de usuario</label>
                <input type="text" id="username" bind:value={username}>

                <label for="contraseña">Contraseña</label>
                <input type="password" id="contraseña" bind:value={contraseña}>

                <button class="botonFormulario" type="submit">Iniciar Sesión</button>
            </form>
        </div>
    </div>
</main>

<style>
    .div-ext{
        background-color: var(--bg-elevated);
        margin: auto;
        margin-top: 170px;
        width: 25%;
        padding: 40px 40px 80px 40px;
        border: solid 1px var(--border-soft);
        border-radius: 12px;
    }
    h1{
        font-size: 40px;
        margin-bottom: 25px;
    }
    .div-form{
        width: 280px;
        margin-left: auto;
        margin-right: auto;
    }
    .botonFormulario {
        display: block;
        width: 280px;
        padding: 12px 24px;
        border: solid 1px var(--border-accent);
        background: var(--border-accent);
        color: var(--text-primary);
        border-radius: 6px;
        font-size: 18px;
        cursor: pointer;
        margin: 30px auto 0;
    }
    button:hover {
        background: color-mix(in srgb, var(--text-secondary) 90%, var(--bg-tertiary));
        transform: scale(1.05);
        transition: all 0.1s;
    }
</style>