<script>
    let email = "";
    let username = "";
    let contraseña = "";
    let birthdate = "";

    async function registro(){
        const response = await fetch("http://localhost:8001/sign_in", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                username: username,
                contrasenha: contraseña,
                fecha_de_nacimiento: birthdate
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("token", data.token);
            localStorage.setItem("id_usuario", data.id_usuario.toString());
            window.location.href = `/usuarios/${data.id_usuario}`;
        } else {
            const error = await response.json();
            alert(error.detail);
        }
    }
</script>

<main>
    <h1>¡Únete a Nexus!</h1>
    <div>
        <form onsubmit={(e) => { e.preventDefault(); registro(); }}>
            <label for="email">Email</label>
            <input type="email" id="email" bind:value={email}>
            
            <label for="username">Nombre de usuario</label>
            <input type="text" id="username" bind:value={username}>

            <label for="password">Contraseña</label>
            <input type="password" id="password" bind:value={contraseña}>

            <label for="birthdate">Fecha de nacimiento</label>
            <input type="date" id="birthdate" bind:value={birthdate}>

            <button class="botonFormulario" type="submit">Registrarse</button>
        </form>
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