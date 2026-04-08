import { redirect } from "@sveltejs/kit";

export async function load({ fetch, cookies, params}) {
    const { id_canal, id_sala } = params;

    const token = cookies.get("access_token");
    
    if (!token) {
        // redirigir al login si no hay token
        redirect(303, "/login");
    }    

    const [resMensajes, resInfoUser, resCanales, resAmigos, resSala, resCanal, resSalas] = await Promise.all([
        fetch(`http://localhost:8001/users/me/channels/${id_canal}/rooms/${id_sala}/messages`),
        fetch(`http://localhost:8001/users/me`),
        fetch(`http://localhost:8001/users/me/channels`),
        fetch(`http://localhost:8001/users/me/friends`),
        fetch(`http://localhost:8001/users/me/channels/${id_canal}/rooms/${id_sala}`),
        fetch(`http://localhost:8001/users/me/channels/${id_canal}`),
        fetch(`http://localhost:8001/users/me/channels/${id_canal}/rooms`)
    ]);

    
    if (resMensajes.status === 401 || resInfoUser.status === 401 || resCanales.status === 401 || resAmigos.status === 401 || resSala.status === 401 || resCanal.status === 401 || resSalas.status === 401) {
        redirect(303, "/login");
    }


    const mensajes = resMensajes.ok ? await resMensajes.json() : [];
    const infoUser = resInfoUser.ok ? await resInfoUser.json(): {};
    const canales = resCanales.ok ? await resCanales.json(): [];
    const amigos = resAmigos.ok ? await resAmigos.json(): [];
    const infoSala = resSala.ok ? await resSala.json(): {};
    const canal = resCanal.ok ? await resCanal.json(): {};
    const salas = resSalas.ok ? await resSalas.json(): {};

    return { id_canal, id_sala, mensajes, infoUser, canales, amigos, infoSala, canal, salas };
}