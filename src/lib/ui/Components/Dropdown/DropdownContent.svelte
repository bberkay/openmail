<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<div class="dropdown-content hidden">
    {@render children()}
</div>

<style>
    :global {
        .dropdown-content {
            position: absolute;
            display: flex;
            background-color: var(--color-border-subtle);
            color: var(--color-text-primary);
            flex-direction: column;
            padding: 1px;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            right: -80px;
            top: 30px;
            width: 100px;

            &.hidden {
                display: none;
            }
        }
    }
</style>
