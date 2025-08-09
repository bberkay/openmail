<script lang="ts">
    interface Props {
        groupDate: string;
    }

    let { groupDate }: Props = $props();
</script>

<div class="email-preview-group-separator">
    <div class="timeline-label">
        <span>{groupDate}</span>
    </div>
</div>

<style>
    :global {
        .mailbox .email-preview-group-separator {
            width: 100%;
            color: var(--color-text-secondary);
            font-size: var(--font-size-sm);
            padding: var(--spacing-sm);
            padding-bottom: calc(var(--spacing-sm) / 1.3);
            text-align: center;
            border-bottom: 1px solid var(--color-border-subtle);

            & .timeline-label {
                font-weight: var(--font-weight-bold);
                text-transform: uppercase;
            }
        }
    }
</style>
