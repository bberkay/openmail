<script lang="ts">
    import { onMount } from "svelte";
    import { type Email } from "$lib/types";
    import Badge from "$lib/ui/Components/Badge";

    interface Props {
        email: Email;
    }

    let { email }: Props = $props();
</script>

<div class="tags">
    {#if Object.hasOwn(email, "flags") && email.flags}
        {#each email.flags as flag}
            <Badge content={flag} />
        {/each}
    {/if}
</div>
