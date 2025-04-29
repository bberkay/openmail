<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        size?: "small" | "medium" | "large";
        [attribute: string]: unknown;
    }

    let {
        size = "medium",
        ...attributes
    }: Props = $props();


    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<small class={combine(`spinner ${size}`, additionalClass)} {...restAttributes}></small>

<style>
    .spinner {
        border: 2px solid var(--color-border);
        border-radius: 50%;
        border-top: 2px solid var(--color-text-primary);
        -webkit-animation: spin 2s linear infinite;
        animation: spin 2s linear infinite;
        display: inline-block;
        margin-right: var(--spacing-2xs);

        &.small {
            width: var(--font-size-xs);
            height: var(--font-size-xs);
            border-width: 2px;
            -webkit-animation-duration: 2s;
            animation-duration: 2s;
        }

        &.medium {
            width: var(--font-size-lg);
            height: var(--font-size-lg);
            border-width: 4px;
            -webkit-animation-duration: 1.25s;
            animation-duration: 1.25s;
        }

        &.large {
            width: var(--font-size-2xl);
            height: var(--font-size-2xl);
            border-width: 6px;
            -webkit-animation-duration: 1s;
            animation-duration: 1s;
        }
    }

    @-webkit-keyframes spin {
        0% { -webkit-transform: rotate(0deg); }
        100% { -webkit-transform: rotate(360deg); }
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
