<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";

    interface  Props {
        onclose: () => void;
        ref?: { abrir: () => void };
    }

    let { onclose, ref = $bindable() }: Props = $props();

    let dialog = $state<HTMLDialogElement | null>(null);
    let nombre_canal = $state("");
    let contenido_principal = $state("");

    $effect(() => {
        ref = {
            abrir: () => {
                nombre_canal = '';
                contenido_principal = '';
                dialog?.showModal();
            }
        };
    });

    function cerrar() {
        dialog?.close();
        onclose();
    }

    async function crear() {
        await fetch(`${PUBLIC_API_URL}/users/me/channels`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre_canal, contenido_principal })
        });
        cerrar();
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