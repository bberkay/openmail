<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        value: string;
        children: Snippet;
    }

    let { value, children }: Props = $props();
</script>

<div class="option" data-value={value}>
    {@render children()}
</div>

<style>
    :global {
        .option {
            padding: var(--spacing-xs) var(--spacing-sm);
            cursor: pointer;
            transition: background-color var(--transition-fast) var(--ease-default);
            color: var(--color-text-secondary);

            &:hover{
                background-color: var(--color-hover);
            }

            &.selected {
                background-color: var(--color-border);
                color: var(--color-text-primary);
            }

            &.hidden {
                opacity: 0;
                visibility: hidden;
            }
        }
    }
</style>
