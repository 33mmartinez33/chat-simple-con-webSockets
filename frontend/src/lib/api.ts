import { error, redirect } from "@sveltejs/kit";
import type { Cookies } from "@sveltejs/kit";

export async function apiFetch(fetchFn: typeof fetch, path: string, cookies?: Cookies) {  
    const res = await fetchFn(path);  
    if (res.status === 401) {
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