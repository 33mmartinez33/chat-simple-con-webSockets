import type { PageServerLoad } from './$types';

// Lee la flash cookie para saber si el usuario llegó aquí por sesión expirada
// La borra inmediatamente después de leerla para que no persista en recargas
// Retorna sesionExpirada: true si la cookie tenía el valor 'sesion_expirada'
export const load: PageServerLoad = async ({ cookies }) => {
    const flash = cookies.get('flash');
    cookies.delete('flash', { path: '/' });
    return { sesionExpirada: flash === 'sesion_expirada' };
};
