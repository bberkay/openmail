<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        content: string;
        [attribute: string]: unknown;
    }

    let {
        content,
        ...attributes
    }: Props  = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<textarea
    class={combine("textarea", additionalClass)}
    {...restAttributes}
>
    {content}
</textarea>

<style>
    :global {
        .textarea {
            background-color: transparent;
            border-radius: 0px;
            border: none;
            border-bottom: 1px solid var(--color-border);
            margin-top: var(--spacing-2xs);
            transition: all var(--transition-fast) var(--ease-default);
            color: var(--color-text-primary);

            &:focus {
                outline: none;
                border-bottom: 1px solid var(--color-text-primary);
            }
        }
    }
</style>
