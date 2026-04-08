<script>
	import { goto } from "$app/navigation";
	import { PUBLIC_API_URL } from "$env/static/public";

    let username = $state("");
    let contraseña = $state("");

    async function login() {
        const response = await fetch(`${PUBLIC_API_URL}/login`, { //consulta el endpoint con esta ruta 
            method: 'POST',
            credentials: "include",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded' // ← esto es lo que espera el backend                
            },
            body: new URLSearchParams({
                username: username,
                password: contraseña
            })
        });

        if (response.ok) {
            // console.log("Redirigiendo a /users/me")
            goto("/users/me"); // Redirige
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