<script lang="ts">
    interface Props {
        onclick: () => void;
        title: string;
    }
    
    let { onclick, title = "Añadir" }: Props = $props();

    
</script>

<button {onclick} {title} class="btn-new">+</button>
<style>
    .btn-new {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        border: 0.5px solid var(--border-accent);
        background: var(--bg-primary);
        color: var(--accent-secondary);
        display: flex;
        align-items: center;
        justify-content: center;
        padding-bottom: 6px;
        cursor: pointer;
        flex-shrink: 0;
        font-size: 1.5rem;
    }
    .btn-new:hover {
        background: color-mix(in srgb, var(--bg-primary) 90%, var(--accent-primary));
        transform: scale(1.05);
        transition: all 0.1s;
    }
</style>