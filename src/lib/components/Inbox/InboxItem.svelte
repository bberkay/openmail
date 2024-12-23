<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { EmailSummary } from "$lib/types";
    import { ApiService, GetRoutes } from "$lib/services/ApiService";

    let { owner, email }: { owner: string; email: EmailSummary } = $props();

    async function getEmailContent(){
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_EMAIL_CONTENT,
            {
                pathParams: {
                    accounts: owner,
                    folder: encodeURIComponent(SharedStore.selectedFolder),
                    uid: email.uid
                }
            }
        );

        if (response.success && response.data) {
            SharedStore.shownEmail = response.data;
        }
    }
</script>

<div>
    <pre>{JSON.stringify(email, null, 2)}</pre>
    <button onclick={getEmailContent} class = "bg-primary">Show Content</button>
    {#if Object.hasOwn(email, "flags") && email.flags}
        {#each email.flags as flag}
            <span class="tag">{flag}</span>
        {/each}
    {/if}
</div>
<br>
