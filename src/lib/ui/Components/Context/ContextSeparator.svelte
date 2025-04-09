<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        [attribute: string]: unknown;
    }

    let {
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<div
    role="separator"
    class={combine("context-menu-separator", additionalClass)}
    {...restAttributes}
></div>

<style>
    .context-menu-separator {
        margin: var(--spacing-2xs) 0;
        height: 1px;
        background-color: var(--color-border);
        width: 100%;
    }
</style>
