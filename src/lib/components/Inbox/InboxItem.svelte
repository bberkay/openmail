<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";
    import { currentEmail } from "$lib/stores";
    import type { OpenMailDataString, OpenMailData, Email } from "$lib/types";

    export let email: Email;

    currentEmail.subscribe(value => {
        if(value.id === email.id){
            email.flags = value.flags;
            document.querySelector(`[data-email-id*="${email.id}"]`)?.setAttribute('data-email-flags', email.flags.join(','));
        }
    });

    async function handleEmailClick(){
        const response: OpenMailDataString = await invoke('get_email_content', { id: email.id });
        const parsedResponse = JSON.parse(response) as OpenMailData;
        if (parsedResponse.success)
            currentEmail.set(parsedResponse.data as Email);
        else
            console.error(parsedResponse);
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="inbox-item" data-email-id={email.id} data-email-flags={email.flags} on:click={handleEmailClick}>
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