<script lang="ts">
    import { sharedStore } from "$lib/stores/shared.svelte";
    import type { EmailWithContent, EmailSummary } from "$lib/types";
    import { ApiService, GetRoutes, PostRoutes, type Response } from "$lib/services/ApiService";

    let { owner, email }: { owner: string; email: EmailSummary } = $props();

    async function getEmailContent(){
        const response: Response = await ApiService.get(
            sharedStore.server,
            GetRoutes.GET_EMAIL_CONTENT,
            {
                pathParams: {
                    accounts: owner,
                    folder: encodeURIComponent(sharedStore.selectedFolder),
                    uid: email.uid
                }
            }
        );

        if (response.success) {
            sharedStore.selectedEmail = response.data as EmailWithContent;
        }
    }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div onclick={getEmailContent}>
    <pre>
        {JSON.stringify(email, null, 2)}
    </pre>
</div>
