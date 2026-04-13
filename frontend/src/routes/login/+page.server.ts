import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies }) => {
    const flash = cookies.get('flash');
    // console.log('flash cookie:', flash, 'todas las cookies:', cookies.getAll());
    cookies.delete('flash', { path: '/' });
    return { sesionExpirada: flash === 'sesion_expirada' };
};