import { PUBLIC_API_URL } from "$env/static/public";
import { apiFetch } from "$lib/api";

// Carga en paralelo los datos del usuario, sus canales y su lista de amigos
// Las cookies se pasan a apiFetch para redirigir a /login si la sesión expiró (401)
// Retorna infoUser, canales y amigos para que estén disponibles en la página y el layout
export async function load({ fetch, cookies }) {
    const [infoUser, canales, amigos] = await Promise.all([
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/friends`, cookies)
    ]);

    return { infoUser, canales, amigos };
}
