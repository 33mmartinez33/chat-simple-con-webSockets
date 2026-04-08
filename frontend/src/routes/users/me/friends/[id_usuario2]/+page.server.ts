import { redirect } from "@sveltejs/kit";

export async function load({ fetch, cookies, params}) {
    const { id_usuario2 } = params;
    const token = cookies.get("access_token");
    if (!token) {
        // redirigir al login si no hay token
         redirect(303, "/login");
    }

    const [resMensajes, resInfoAmigo, resInfoUser, resCanales, resAmigos] = await Promise.all([
        fetch(`http://localhost:8001/users/me/friends/${id_usuario2}/messages`),
        fetch(`http://localhost:8001/users/me/friends/${id_usuario2}`),
        fetch(`http://localhost:8001/users/me`),
        fetch(`http://localhost:8001/users/me/channels`),
        fetch(`http://localhost:8001/users/me/friends`)
    ]);

    if (resMensajes.status === 401 || resInfoAmigo.status === 401 || resInfoUser.status === 401 || resCanales.status === 401 || resAmigos.status === 401) {
        redirect(303, "/login");
    }

    const mensajes = resMensajes.ok ? await resMensajes.json() : [];
    const infoAmigo = resInfoAmigo.ok ? await resInfoAmigo.json() : {};
    const infoUser = resInfoUser.ok ? await resInfoUser.json(): {};
    const canales = resCanales.ok ? await resCanales.json(): [];
    const amigos = resAmigos.ok ? await resAmigos.json(): [];

    return { id_usuario2, mensajes, infoAmigo, infoUser, canales, amigos };
}