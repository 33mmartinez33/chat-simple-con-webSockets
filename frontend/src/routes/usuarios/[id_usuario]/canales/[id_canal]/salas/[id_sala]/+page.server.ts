export async function load({params}) {
    const { id_usuario, id_canal, id_sala } = params;
    
    const [resMensajes, resInfoUser, resCanales, resAmigos, resSala, resCanal, resSalas] = await Promise.all([
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales/${id_canal}/salas/${id_sala}/mensajes`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/amigos`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales/${id_canal}/salas/${id_sala}`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales/${id_canal}`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales/${id_canal}/salas`)
    ]);

    const mensajes = resMensajes.ok ? await resMensajes.json() : [];
    const infoUser = resInfoUser.ok ? await resInfoUser.json(): {};
    const canales = resCanales.ok ? await resCanales.json(): [];
    const amigos = resAmigos.ok ? await resAmigos.json(): [];
    const infoSala = resSala.ok ? await resSala.json(): {};
    const canal = resCanal.ok ? await resCanal.json(): {};
    const salas = resSalas.ok ? await resSalas.json(): {};

    return { id_usuario, id_canal, id_sala, mensajes, infoUser, canales, amigos, infoSala, canal, salas };
}