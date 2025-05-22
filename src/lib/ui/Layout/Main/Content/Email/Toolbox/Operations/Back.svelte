<script lang="ts">
    import { backToDefault } from "$lib/ui/Layout/Main/Content.svelte";
    import * as Button from "$lib/ui/Components/Button";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<Button.Basic
    type="button"
    class="btn-inline"
    style="margin-right: var(--spacing-sm)"
    onclick={() => backToDefault()}
>
    {@render children()}
</Button.Basic>
