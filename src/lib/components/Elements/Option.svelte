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
    .option :global{
        padding: 10px;
        cursor: pointer;
        transition: background-color 0.2s ease;

        &:hover{
            background-color: #f8f9fa;
        }

        &.selected {
            background-color: #e3f2fd;
            color: #007bff;
            font-weight: 500;
        }

        &.hidden {
            opacity: 0;
            visibility: hidden;
        }
    }
</style>
