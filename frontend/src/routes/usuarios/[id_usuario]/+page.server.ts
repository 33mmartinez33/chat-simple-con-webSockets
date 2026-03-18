export async function load({params}) {
    const { id_usuario } = params; //parametros que se obtienen de la ruta

    const [resCanales, resAmigos] = await Promise.all([ //datos que se obtienen de los endpoints
                fetch(`http://localhost:8001/usuarios/${id_usuario}/canales`),
                fetch(`http://localhost:8001/usuarios/${id_usuario}/amigos`)
            ]);
    const canales = resCanales.ok ? await resCanales.json() : []; // Operador ternario, true lista de canales, false un list vacio
    const amigos = resAmigos.ok ?  await resAmigos.json() : [];


    return {canales, amigos, id_usuario};


}