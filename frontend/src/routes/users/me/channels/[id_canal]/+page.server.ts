import { PUBLIC_API_URL } from "$env/static/public";
import { apiFetch } from "$lib/api.js";

export async function load({params, fetch, cookies}) {
    const {  id_canal } = params;

    // fetch automaticamente envia las cookies al backend, el cual comprueba el jwt de la cookies acces_token
    // cookies se utiliza para en caso de que haya una redireccion al /login por fin de sesion, se transmite la informacion al page.server del /login la cookie flash seteada en api.ts cunado se detecta un error que devuelve el backend con 401, no autorizado (token inválido)

    const [ infoUser, canales, salas, amigos, canal] = await Promise.all([
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels/${id_canal}/rooms`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/friends`, cookies),
        apiFetch(fetch, `${PUBLIC_API_URL}/users/me/channels/${id_canal}`, cookies),

    ]);


    return { id_canal, infoUser, canales, salas, amigos, canal};
}