export async function load({params}) {
    const { id_usuario, id_usuario2 } = params;
    
    const resMensajes = await fetch(`/usuarios/${id_usuario}/amigos/${id_usuario2}`);
    const mensajes = resMensajes.ok ? await resMensajes.json() : [];

    return {id_usuario, id_usuario2, mensajes}
}