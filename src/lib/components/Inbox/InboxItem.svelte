<script lang="ts">
    import { sharedStore } from "$lib/stores/shared.svelte";
    import type { Response, Email } from "$lib/types";

    let { owner, email } = $props();

    $effect(() => {
        if(sharedStore.selectedEmail && sharedStore.selectedEmail.uid === email.uid){
            email.flags = sharedStore.selectedEmail.flags;
            document.querySelector(`[data-email-uid*="${email.uid}"]`)?.setAttribute(
                'data-email-flags', 
                email.flags.join(',')
            );
        }
    })

    async function handleEmailClick(){
        const response: Response = await fetch(`${
                sharedStore.server
            }/get-email-content/${
                owner
            }/${
                encodeURIComponent(sharedStore.selectedFolder)
            }/${
                email.uid
            }`).then(res => res.json());
        if (response.success) {
            sharedStore.selectedEmail = response.data as Email;
        } else {
            console.error(response);
        }
    }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="inbox-item" data-email-owner={owner} data-email-uid={email.uid} data-email-flags={email.flags} onclick={handleEmailClick}>
    <h3>{email.from}</h3>
    <small>
        <span>{email.date}</span> &lt;<span>{email.to}</span>&gt;
    </small>
    <br>
    <small>{email.subject}</small>
    <br>
    <small>{email.body_short}</small>
</div>

<style>
    .inbox-item{
        border: none;
        padding: 1rem 0.5rem;
        margin-bottom: 0.1rem;
        cursor: pointer;
        background-color: #414040;

        &[data-email-flags*="Seen"], &[data-email-flags*="seen"]{
           background-color: #2c2c2c;
        }

        &[data-email-flags*="Flagged"], &[data-email-flags*="flagged"]{
            background-color: #f8f3c7;
            color: #121212;

            &:hover{
                background-color: #f8f4d4;
            }
        }

        &:hover{
            filter: brightness(1.1);
        }

        &:active{
            filter: brightness(1);
        }
    }
</style>
