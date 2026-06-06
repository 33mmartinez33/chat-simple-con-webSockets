import { writable } from "svelte/store";

// Tipo que representa una notificación recibida del servidor
// tipo "sala": mensaje en un canal; tipo "dm": mensaje directo
type Notificacion = {
    id_notificacion: number;
    contenido: string;
    id_mensaje: number;
    tipo: 'sala' | 'dm';
    id_sala?: number;           // Presente si tipo === 'sala'
    id_canal?: number;          // Presente si tipo === 'sala'
    id_usuario_emisor?: number; // Presente si tipo === 'dm'
};

// Store global con las notificaciones no leídas del usuario activo
// Se actualiza en tiempo real desde el WebSocket de notificaciones
export const notificaciones = writable<Notificacion[]>([]);
