import { PUBLIC_API_URL } from "$env/static/public";
import { apiFetch } from "$lib/api.js";

export async function load({ fetch, params, cookies }) {
    const { id_usuario2 } = params;

    const [mensajes, infoAmigo, infoUser, canales, amigos] = await Promise.all([
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/friends/${id_usuario2}/messages`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/friends/${id_usuario2}`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/friends`, cookies)
    ]);


    return { id_usuario2: Number(id_usuario2), mensajes, infoAmigo, infoUser, canales, amigos };
}