export async function load({params}) {
    const { id_usuario, id_canal } = params;
    
    const [ resInfoUser, resCanales, resSalas, resAmigos, resCanal] = await Promise.all([
        fetch(`http://localhost:8001/usuarios/${id_usuario}`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales/${id_canal}/salas`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/amigos`),
        fetch(`http://localhost:8001/usuarios/${id_usuario}/canales/${id_canal}`),

    ]);

    const infoUser = resInfoUser.ok ? await resInfoUser.json(): {};
    const canales = resCanales.ok ? await resCanales.json(): [];
    const salas = resSalas.ok ? await resSalas.json(): [];
    const amigos = resAmigos.ok ? await resAmigos.json(): [];
    const canal = resCanal.ok ? await resCanal.json(): {};

    return { id_usuario, id_canal, infoUser, canales, salas, amigos, canal};
}