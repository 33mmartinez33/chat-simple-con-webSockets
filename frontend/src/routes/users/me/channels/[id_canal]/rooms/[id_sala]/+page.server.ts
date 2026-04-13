import { PUBLIC_API_URL } from "$env/static/public";
import { apiFetch } from "$lib/api.js";

export async function load({ fetch, params, cookies }) {
    const { id_canal, id_sala } = params;


    const [mensajes, infoUser, canales, amigos, infoSala, canal, salas] = await Promise.all([
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels/${id_canal}/rooms/${id_sala}/messages`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/friends`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels/${id_canal}/rooms/${id_sala}`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels/${id_canal}`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels/${id_canal}/rooms`, cookies)
    ]);



    return { id_canal, id_sala, mensajes, infoUser, canales, amigos, infoSala, canal, salas };
}