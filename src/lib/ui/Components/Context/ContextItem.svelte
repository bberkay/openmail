<script lang="ts">
    import { type Snippet } from "svelte";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        onclick: (((e: Event) => void) | ((e: Event) => Promise<void>));
        children: Snippet;
    }

    let { onclick, children }: Props = $props();
</script>

<div class="context-menu-item">
    <Button.Basic
        type="button"
        class="btn-inline"
        style="width: 100%"
        {onclick}
    >
        {@render children()}
    </Button.Basic>
</div>

<style>
    .context-menu-item {
        padding: 0 var(--spacing-2xs);
    }
</style>
