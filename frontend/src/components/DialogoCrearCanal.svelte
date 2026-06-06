<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";
	import { toast } from 'svelte-sonner';

    // Diálogo para crear un nuevo canal con nombre y contenido principal
    interface Props {
        onclose: () => void;         // Callback al cerrar (se usa para invalidar datos del padre)
        ref?: { abrir: () => void }; // Referencia externa para abrir el diálogo desde el padre
    }

    let { onclose, ref = $bindable() }: Props = $props();

    let dialog = $state<HTMLDialogElement | null>(null);
    let nombre_canal = $state("");
    let contenido_principal = $state("");

    // Expone el método abrir() al componente padre y limpia los campos al abrirse
    $effect(() => {
        ref = {
            abrir: () => {
                nombre_canal = '';
                contenido_principal = '';
                dialog?.showModal();
            }
        };
    });

    // Cierra el diálogo y notifica al padre para que recargue los datos
    function cerrar() {
        dialog?.close();
        onclose();
    }

    // Envía la petición de creación del canal y cierra el diálogo si fue exitosa
    // Muestra un toast de error si el nombre ya existe o hay un fallo de red
    async function crear() {
        try {
            const res = await fetch(`${PUBLIC_API_URL}/users/me/channels`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre_canal, contenido_principal })
            });
            if (!res.ok) {
                const data = await res.json();
                toast.error(data.detail ?? 'Error al crear el canal');
                return;
            }
            cerrar();
        } catch {
            toast.error('Error de conexión');
        }
    }
</script>

<dialog bind:this={dialog}>
<div class="modal-header">
        <h3>Crear canal</h3>
        <button class="btn-cerrar" onclick={cerrar}>✕</button>
    </div>

    <input type="text" placeholder="Nombre del canal" maxlength="14" bind:value={nombre_canal} />

    <textarea id="input-contenido" placeholder="Contenido principal (post) del canal" bind:value={contenido_principal}></textarea>
    <button class="btn-crear" onclick={crear}>Crear</button>
</dialog>

<style>
    .btn-crear {
        color: var(--text-primary);
        margin: auto;
        margin-top: 16px;
        border-radius: 20px;
        border: 1px solid var(--border-accent);
        padding: 6px 24px;
        display: block;
        background: none;
        cursor: pointer;
    }
    #input-contenido{
        height: 180px;
    }

</style>