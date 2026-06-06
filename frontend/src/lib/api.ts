import { error, redirect } from "@sveltejs/kit";
import type { Cookies } from "@sveltejs/kit";

// Wrapper centralizado para llamadas a la API que gestiona sesión expirada y errores HTTP
// Parámetros:
//   fetchFn: instancia de fetch (la del servidor en +page.server.ts o la del navegador)
//   path: URL del endpoint a llamar
//   cookies: objeto de cookies de SvelteKit (solo necesario en el servidor para establecer la flash cookie)
// Retorna el JSON de la respuesta si la llamada fue exitosa
// Redirige a /login con flash cookie si el servidor devuelve 401
// Lanza un error de SvelteKit para cualquier otro status no OK
export async function apiFetch(fetchFn: typeof fetch, path: string, cookies?: Cookies) {
    const res = await fetchFn(path);
    if (res.status === 401) {
        // Se guarda una cookie flash de corta duración para mostrar el aviso de sesión expirada en la pantalla de login
        cookies?.set('flash', 'sesion_expirada', {
            path: '/',
            maxAge: 10,
            httpOnly: true,
            sameSite: 'strict'
        });
        redirect(303, '/login');
    }

    if (!res.ok) error(res.status, res.statusText);
    return res.json();
}
