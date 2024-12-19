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

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div onclick={getEmailContent}>
    <pre>{JSON.stringify(email, null, 2)}</pre>
</div>
<br>
