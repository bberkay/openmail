<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();
</script>

<div
    class="dropdown-toggle-container"
    role="button"
    tabindex="0"
    {...attributes}
>
    <span style="display:none;">#dt#</span>
    {@render children()}
</div>
