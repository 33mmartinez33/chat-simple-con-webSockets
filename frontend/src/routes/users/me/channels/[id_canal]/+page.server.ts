import { redirect } from "@sveltejs/kit";

export async function load({params, fetch, cookies}) {
    const {  id_canal } = params;
    
        const token = cookies.get("access_token");
        
        if (!token) {
            // redirigir al login si no hay token
            redirect(303, "/login");
        }

    const [ resInfoUser, resCanales, resSalas, resAmigos, resCanal] = await Promise.all([
        fetch(`http://localhost:8001/users/me`),
        fetch(`http://localhost:8001/users/me/channels`),
        fetch(`http://localhost:8001/users/me/channels/${id_canal}/rooms`),
        fetch(`http://localhost:8001/users/me/friends`),
        fetch(`http://localhost:8001/users/me/channels/${id_canal}`),

    ]);

    if (resInfoUser.status === 401 || resCanales.status === 401 || resSalas.status === 401 || resAmigos.status === 401 || resCanal.status === 401) {
        redirect(303, "/login");
    }

    const infoUser = resInfoUser.ok ? await resInfoUser.json(): {};
    const canales = resCanales.ok ? await resCanales.json(): [];
    const salas = resSalas.ok ? await resSalas.json(): [];
    const amigos = resAmigos.ok ? await resAmigos.json(): [];
    const canal = resCanal.ok ? await resCanal.json(): {};

    return { id_canal, infoUser, canales, salas, amigos, canal};
}