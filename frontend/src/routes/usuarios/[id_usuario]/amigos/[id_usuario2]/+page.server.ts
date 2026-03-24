export async function load({params}) {
    const { id_usuario, id_usuario2 } = params;
    
    const [resMensajes, resInfoAmigo, resInfoUser, resCanales, resAmigos] = await Promise.all([
        fetch(`http://localhost:8001/usuarios/${id_usuario}/amigos/${id_usuario2}`),
        fetch(`http://localhost:8001/usuarios/${id_usuario2}`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/amigos`)
    ]);

    const mensajes = resMensajes.ok ? await resMensajes.json() : [];
    const infoAmigo = resInfoAmigo.ok ? await resInfoAmigo.json() : {};
    const infoUser = resInfoUser.ok ? await resInfoUser.json(): {};
    const canales = resCanales.ok ? await resCanales.json(): [];
    const amigos = resAmigos.ok ? await resAmigos.json(): [];

    return { id_usuario, id_usuario2, mensajes, infoAmigo, infoUser, canales, amigos };
}