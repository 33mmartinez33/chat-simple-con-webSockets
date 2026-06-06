<script lang="ts">
    // Diálogo reutilizable para buscar y añadir un ítem (canal o amigo) desde la API
    interface Props {
        endpoint: string;           // URL base del endpoint de búsqueda (se añade ?q=...)
        titulo: string;             // Título que se muestra en la cabecera del diálogo
        labelNombre: string;        // Clave del objeto resultado que contiene el nombre a mostrar
        onclose: () => void;        // Callback al cerrar el diálogo
        onAnhadir: (item: any) => Promise<void>; // Callback al confirmar el añadido de un ítem
        ref?: { abrir: () => void }; // Referencia externa para abrir el diálogo desde el padre
    }

    let { endpoint, titulo, labelNombre, onclose, onAnhadir, ref = $bindable() }: Props = $props();

    let dialog = $state<HTMLDialogElement | null>(null);
    let busqueda = $state('');
    let filtrados = $state<any[]>([]);
    let timeout: any;

    // Expone el método abrir() al componente padre mediante ref bindable
    $effect(() => {
        ref = {
            abrir: () => {
                busqueda = '';
                filtrados = [];
                dialog?.showModal();
            }
        };
    });

    // Busca en el endpoint con debounce de 300ms para evitar llamadas por cada tecla
    // Solo lanza la búsqueda si el texto tiene al menos 2 caracteres
    async function buscar() {
        clearTimeout(timeout);
        if (busqueda.length < 2) { filtrados = []; return; }
        timeout = setTimeout(async () => {
            try {
                const res = await fetch(`${endpoint}?q=${encodeURIComponent(busqueda)}`, { credentials: 'include' });
                if (res.ok) filtrados = await res.json();
            } catch {
                filtrados = [];
            }
        }, 300);
    }

    // Cierra el diálogo, limpia la búsqueda y llama al callback onclose
    function cerrar() {
        dialog?.close();
        busqueda = '';
        onclose();
    }

    // Ejecuta el callback onAnhadir con el ítem seleccionado y luego cierra el diálogo
    // Parámetros: item: objeto del resultado seleccionado
    async function anhadir(item: any) {
        await onAnhadir(item);
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

<style>
    .resultado-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 10px;
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.15s;
    }

    .resultado-item:hover {
        background: color-mix(in srgb, var(--bg-tertiary) 60%, var(--accent-tertiary));
    }
</style>