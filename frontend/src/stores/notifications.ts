import { writable } from "svelte/store";

type Notificacion = {
    id_notificacion: number;
    contenido: string;
    id_mensaje: number;
    tipo: 'sala' | 'dm';
    id_sala?: number;
    id_canal?: number;
    id_usuario_emisor?: number;
};

export const notificaciones = writable<Notificacion[]>([]);