<script>
	import { goto } from "$app/navigation";
	import { PUBLIC_API_URL } from "$env/static/public";

    let email = $state("");
    let username = $state("");
    let contraseña = $state("");
    let birthdate = $state("");

    async function registro(){
        const response = await fetch(`${PUBLIC_API_URL}/sign_in`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                username: username,
                password: contraseña,
                fecha_de_nacimiento: birthdate
            })
        });

        if (response.ok) {
            console.log("Respuesta ok: ", response)
            goto("/users/me");
        } else {
            const error = await response.json();
            alert(error.detail);
        }
    }
</script>

<main>
    <div class="div-ext">
        <h1>¡Únete a Nexus!</h1>
        <div class="div-form">
            <form onsubmit={(e) => { e.preventDefault(); registro(); }}>
                <label for="email">Email</label>
                <input type="email" id="email" bind:value={email} minlength="8" maxlength="25">
                
                <label for="username">Nombre de usuario</label>
                <input type="text" id="username" bind:value={username} minlength="3" maxlength="16">

                <label for="password">Contraseña</label>
                <input type="password" id="password" bind:value={contraseña} minlength="6" maxlength="20">

                <label for="birthdate">Fecha de nacimiento</label>
                <input type="date" id="birthdate" bind:value={birthdate}>

                <button class="botonFormulario" type="submit">Registrarse</button>
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
/* Invierte el color del icono del calendario de negro a blanco*/
    input[type="date"]::-webkit-calendar-picker-indicator {
        filter: invert(1);
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
    }
    button:hover {
        background: color-mix(in srgb, var(--text-secondary) 90%, var(--bg-tertiary));
        transform: scale(1.05);
        transition: all 0.1s;
    }
</style>