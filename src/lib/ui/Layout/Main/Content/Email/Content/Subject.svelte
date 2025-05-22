<script lang="ts">
    import { onMount } from "svelte";
    import { type Email } from "$lib/types";

    interface Props {
        email: Email;
    }

    let { email }: Props = $props();
</script>

<div class="subject">
    {email.subject || ""}
</div>

<style>
    :global {
        .email-content .subject {
            margin-top: var(--spacing-md);
            display: flex;
            flex-direction: column;
            font-size: var(--font-size-lg);
        }
    }
</style>
