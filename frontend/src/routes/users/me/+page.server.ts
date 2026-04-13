import { PUBLIC_API_URL } from "$env/static/public";
import { apiFetch } from "$lib/api";

export async function load({ fetch, cookies }) {
    const [infoUser, canales, amigos] = await Promise.all([
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me`, cookies), // las cookies se envian al apifetch para que valide, en caso de error 401 si es producido por sesion expirada
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/friends`, cookies)
    ]);

    return { infoUser, canales, amigos };
}