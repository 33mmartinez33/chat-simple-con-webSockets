<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";

    interface  Props {
        id_canal: number;
        onclose: () => void;
        ref?: { abrir: () => void };
    }

    let { id_canal, onclose, ref = $bindable() }: Props = $props();

    let dialog = $state<HTMLDialogElement | null>(null);
    let nombre_sala = $state("");
    let tipo = $state("texto");

    $effect(() => {
        ref = {
            abrir: () => {
                nombre_sala = '';
                tipo = 'texto';
                dialog?.showModal();
            }
        };
    });

    function cerrar() {
        dialog?.close();
        onclose();
    }

    async function crear() {
        await fetch(`${PUBLIC_API_URL}/users/me/channels/${id_canal}/rooms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre_sala, tipo })
        });
        cerrar();
}
</script>

<dialog bind:this={dialog}>
<div class="modal-header">
        <h3>Crear sala</h3>
        <button class="btn-cerrar" onclick={cerrar}>✕</button>
    </div>

    <input type="text" placeholder="Nombre de la sala" bind:value={nombre_sala} />

    <select bind:value={tipo}>
        <option value="texto">Texto</option>
        <option value="voz">Voz</option>
    </select>

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

select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-accent);
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  margin-bottom: 1rem;
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}
</style>