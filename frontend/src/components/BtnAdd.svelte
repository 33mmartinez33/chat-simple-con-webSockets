<script lang="ts">
    interface Props {
        onclick: () => void;
        title: string;
    }
    
    let { onclick, title = "Añadir" }: Props = $props();
</script>