<script lang="ts">
    interface Props {
        onclick: () => void;
        title: string;
    }
    
    let { onclick, title = "Añadir" }: Props = $props();

    
</script>

<button {onclick} {title} class="btn-add">New</button>
<style>
        .btn-add {
        width: 48px;
        height: 34px;
        border-radius: 6px;
        border: 0.5px solid var(--border-accent);
        background: var(--bg-primary);
        color: var(--accent-secondary);
        display: flex;
        align-items: center;
        justify-content: center;
        padding-bottom: 2px;
        cursor: pointer;
        flex-shrink: 0;
        font-size: 0.8rem;
    }
    .btn-add:hover {
    background: color-mix(in srgb, var(--bg-primary) 90%, var(--accent-primary));
    transform: scale(1.05);
    transition: all 0.1s;
}
</style>