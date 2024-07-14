<script lang="ts">
    import { onMount } from 'svelte';
    import { invoke } from "@tauri-apps/api/core";
    import type { OpenMailData, OpenMailDataString } from '$lib/types';

    let receivers: HTMLElement;
    let sendEmailButton: HTMLButtonElement;
    let body: WYSIWYGEditor;
    onMount(() => {
        // @ts-ignore
        body = new WYSIWYGEditor('body');
        body.init();
        
        receivers = document.querySelector('.tags')!;
        sendEmailButton = document.querySelector('#send-email-form button[type="submit"]')!;
    });

    function handleReceivers(e: KeyboardEvent){
        const target = e.target as HTMLInputElement;
        const isEmailValid = target.value.match(/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/);
        if((e.key === 'Spacebar' || e.key === ' ')){
            if(target.value !== '' && isEmailValid){
                receivers.style.display = 'flex';
                receivers.innerHTML += `<span>${target.value}<button onclick="this.parentElement.remove()"></button></span>`;
                target.value = '';
            }
            else{
                target.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    target.style.transform = 'scale(1)';
                }, 100);
            }
        }
    }

    function getFormKeyValues(){
        return {
            "receivers": Array.from(document.getElementById('receiver_emails')!.parentElement!.querySelectorAll(".tags span")).map(span => span.textContent),
            "subject": (document.getElementById('subject') as HTMLInputElement).value,
            "body": body.getHTMLContent(),
            "attachments": (document.getElementById('attachments') as HTMLInputElement).files,
        }
    }

    async function handleSendEmail(){
        sendEmailButton.disabled = true;
        sendEmailButton.textContent = 'Sending...';
        let response: OpenMailDataString = await invoke('send_email', getFormKeyValues());
        try{
            let parseResponse = JSON.parse(response) as OpenMailData;
            if(parseResponse.success){
                // Show alert
            }
            sendEmailButton.disabled = false;
            sendEmailButton.textContent = "Send";
        }catch{
            console.error(response);
        }
    }
</script>

<section class="send-email">
    <div class="card">
        <form id="send-email-form" on:submit|preventDefault={handleSendEmail}>
            <div class="form-group">
                <label for="receiver_emails">Receiver(s)</label>
                <input type="email" name="receiver_emails" id="receiver_emails" on:keyup={handleReceivers}>
                <div class="tags" tabindex="-1">
                    <!-- Receivers -->
                </div>
            </div>
            <div class="form-group">
                <label for="subject">Subject</label>
                <input type="text" name="subject" id="subject" required>
            </div>
            <div class="form-group">
                <label for="body">Body</label>
                <div id="body"></div>
            </div>
            <div class="form-group">
                <label for="attachments">Attachment(s)</label>
                <input type="file" name="attachments" id="attachments" multiple>
            </div>
            <input type="number" name="message_id" tabindex="-1" hidden>
            <button type="submit">Send</button>
        </form>
    </div>
</section>
