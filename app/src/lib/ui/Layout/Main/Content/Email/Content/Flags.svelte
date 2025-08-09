<script lang="ts">
    import { type Email } from "$lib/types";
    import Badge from "$lib/ui/Components/Badge";

    interface Props {
        email: Email;
    }

    let { email }: Props = $props();
</script>

{#if Object.hasOwn(email, "flags") && email.flags && email.flags.length > 0}
    <div class="tags flags">
        {#each email.flags as flag}
            <Badge content={flag} />
        {/each}
    </div>
{/if}

<style>
    :global {
        .email-content .flags {
            margin-bottom: var(--spacing-md);
        }
    }
</style>
