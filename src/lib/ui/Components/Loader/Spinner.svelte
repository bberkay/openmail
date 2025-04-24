<script lang="ts">
    interface Props {
        text?: string;
        [attribute: string]: unknown;
    }

    let {
        text,
        ...attributes
    }: Props = $props();
</script>

<span {...attributes}>
    <small class="loader"></small>
    {#if text}
        {text}
    {/if}
</span>

<style>
    .loader {
        border: 2px solid var(--color-border);
        border-radius: 50%;
        border-top: 2px solid var(--color-text-primary);
        width: 10px;
        height: 10px;
        -webkit-animation: spin 2s linear infinite;
        animation: spin 2s linear infinite;
        display: inline-block;
        margin-right: var(--spacing-2xs);
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
