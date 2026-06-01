<script lang="ts">
    import { onDestroy, onMount, type Snippet } from 'svelte';
    import { PUBLIC_API_URL, PUBLIC_WS_URL } from '$env/static/public';
    import { toast, Toaster } from 'svelte-sonner';
    import { notificaciones } from '../../../stores/notifications';

    let { children }: { children: Snippet } = $props();
    let ws: WebSocket;
    let cerradoManualmente = false;

    function agregar(notif: any) {
        notificaciones.update(n =>
            n.some(x => x.id_notificacion === notif.id_notificacion) ? n : [...n, notif]
        );
    }

    async function cargarPendientes() {
        try {
            const res = await fetch(`${PUBLIC_API_URL}/users/me/notifications`, { credentials: 'include' });
            if (res.ok) {
                const data = await res.json();
                notificaciones.set(data);
            }
        } catch {}
    }

    function conectar() {
        ws = new WebSocket(`${PUBLIC_WS_URL}/ws/users/me/notifications`);

        ws.onmessage = (event) => {
            const notif = JSON.parse(event.data);
            agregar(notif);
            toast.info(notif.contenido);
        };

        ws.onerror = () => {
            toast.error('Error de conexión con notificaciones');
        };

        ws.onclose = () => {
            if (!cerradoManualmente) {
                setTimeout(conectar, 3000);
            }
        };
    }

    onMount(async () => {
        await cargarPendientes();
        conectar();
    });

    onDestroy(() => {
        cerradoManualmente = true;
        ws?.close();
    });
</script>

<Toaster />
{@render children()}