import { redirect } from "@sveltejs/kit";

export async function load({ fetch, cookies }) {
    const token = cookies.get("access_token");
    
    if (!token) {
        // redirigir al login si no hay token
        redirect(303, "/login");
    }
    const [resUser, resCanales, resAmigos] = await Promise.all([ //datos que se obtienen de los endpoints
        fetch(`http://localhost:8001/users/me`),        
        fetch(`http://localhost:8001/users/me/channels`),
        fetch(`http://localhost:8001/users/me/friends`)
    ]);

    if (resUser.status === 401 || resCanales.status === 401 || resAmigos.status === 401) {
        redirect(303, "/login");
    }

    const infoUser = resUser.ok? await resUser.json() : {};
    const canales = resCanales.ok ? await resCanales.json() : []; // Operador ternario, true lista de canales, false un list vacio
    const amigos = resAmigos.ok ?  await resAmigos.json() : [];


    return { infoUser, canales, amigos};


}