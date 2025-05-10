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
    class={combine("separator", additionalClass)}
    {...restAttributes}
></div>
