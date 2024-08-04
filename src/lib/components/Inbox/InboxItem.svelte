<script lang="ts">
    import { currentEmail, currentFolder, serverUrl } from "$lib/stores";
    import type { OpenMailData, Email } from "$lib/types";
    import { get } from "svelte/store";

    export let email: Email;

    currentEmail.subscribe(value => {
        if(value.uid === email.uid){
            email.flags = value.flags;
            document.querySelector(`[data-email-uid*="${email.uid}"]`)?.setAttribute('data-email-flags', email.flags.join(','));
        }
    });

    async function handleEmailClick(){
        const response: OpenMailData = await fetch(`${get(serverUrl)}/get-email-content/${encodeURIComponent(get(currentFolder))}/${email.uid}`).then(res => res.json());
        if (response.success)
            currentEmail.set(response.data as Email);
        else
            console.error(response);
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="inbox-item" data-email-uid={email.uid} data-email-flags={email.flags} on:click={handleEmailClick}>
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
