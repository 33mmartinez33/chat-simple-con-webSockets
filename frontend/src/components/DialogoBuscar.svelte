<script lang="ts">
    interface Props {
        endpoint: string;
        titulo: string;
        labelNombre: string;
        onclose: () => void;
        onAnhadir: (item: any) => Promise<void>;
        ref?: { abrir: () => void };
    }

    let { endpoint, titulo, labelNombre, onclose, onAnhadir, ref = $bindable() }: Props = $props();

    let dialog = $state<HTMLDialogElement | null>(null);
    let busqueda = $state('');
    let filtrados = $state<any[]>([]);
    let timeout: any;

    $effect(() => {
        ref = {
            abrir: () => {
                busqueda = '';
                filtrados = [];
                dialog?.showModal();
            }
        };
    });

    async function buscar() {
        clearTimeout(timeout);
        if (busqueda.length < 2) { filtrados = []; return; }
        timeout = setTimeout(async () => {
            const res = await fetch(`${endpoint}?q=${encodeURIComponent(busqueda)}`, {credentials: "include"});
            filtrados = await res.json();
        }, 300);
    }

    function cerrar() {
        dialog?.close();
        busqueda = '';
        onclose();
    }

    async function anhadir(item: any) {
        await onAnhadir(item)
        cerrar();
    }
</script>

<dialog bind:this={dialog}>
    <div class="modal-header">
        <h3>{titulo}</h3>
        <button class="btn-cerrar" onclick={cerrar}>✕</button>
    </div>

    <input
        type="text"
        placeholder= "Buscar..."
        bind:value={busqueda}
        oninput={buscar}
    />

    <div class="resultados">
        {#if busqueda.length < 2}
            <p class="hint">Escribe al menos 2 caracteres</p>
        {:else if filtrados.length === 0}
            <p class="hint">No se encontró ningún resultado</p>
        {:else}
            {#each filtrados as item}
                <div class="resultado-item">
                    <span>{item[labelNombre]}</span>
                    <button onclick={() => anhadir(item)}>Añadir</button>
                </div>
            {/each}
        {/if}
    </div>
</dialog>