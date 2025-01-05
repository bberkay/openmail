<script lang="ts">
    import { mount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { EmailSummary } from "$lib/types";
    import { ApiService, GetRoutes } from "$lib/services/ApiService";

    let { owner, email }: { owner: string; email: EmailSummary } = $props();

    async function getEmailContent(event: Event){
        const getEmailContentBtn = event.target as HTMLButtonElement;
        getEmailContentBtn.disabled = true;
        getEmailContentBtn.innerText = '';
        const loader = mount(Loader, {
            target: getEmailContentBtn,
        });

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
        } else {
            alert(response.message);
        }

        getEmailContentBtn.disabled = false;
        unmount(loader);
        getEmailContentBtn.innerHTML = 'Show Content';
    }
</script>

<div>
    <pre>{JSON.stringify(email, null, 2)}</pre>
    <button onclick={getEmailContent} class = "bg-primary" style="margin-top:10px;">Show Content</button>
    {#if Object.hasOwn(email, "flags") && email.flags}
        {#each email.flags as flag}
            <span class="tag">{flag}</span>
        {/each}
    {/if}
</div>
<br>
