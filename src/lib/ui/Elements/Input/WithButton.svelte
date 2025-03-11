<script lang="ts">
    import { type Snippet } from "svelte";

    interface Props {
        type: string;
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        type,
        children,
        ...attributes
    }: Props  = $props();
</script>

<div class="input-with-button">
    <input {...attributes} {type}>
    <div>
        <button type="button" class="inline">
            {@render children()}
        </button>
    </div>
</div>

<style>

</style>
