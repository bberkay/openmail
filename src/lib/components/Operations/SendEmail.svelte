<script lang="ts">
    import { onMount } from 'svelte';
    import { invoke } from "@tauri-apps/api/core";
    import type { OpenMailData, OpenMailDataString } from '$lib/types';

    // @ts-ignore
    let body: WYSIWYGEditor;
    let receivers: HTMLElement;
    let sendEmailButton: HTMLButtonElement;
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

    function getFormKeyValues() {
        return {
            "receivers": Array.from(document.getElementById('receiver_emails')!.parentElement!.querySelectorAll(".tags span")).map(span => span.textContent).join(","),
            "subject": (document.getElementById('subject') as HTMLInputElement).value,
            "body": body.getHTMLContent(),
            //"attachments": Array.from((document.getElementById('attachments') as HTMLInputElement).files || []),
        }
    }

    function fileToBase64(file: File): Promise<{ filename: string, size: number, data: string }> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve({ filename: file.name, size: file.size, data: reader.result as string });
            reader.onerror = error => reject(error);
        });
    }

    async function handleSendEmail(e: Event){
        sendEmailButton.disabled = true;
        sendEmailButton.textContent = 'Sending...';
        const formData = getFormKeyValues();
        /*if(formData.attachments.length > 0){
            formData.attachments = await Promise.all(formData.attachments.map(fileToBase64));
            formData.attachments = JSON.stringify(formData.attachments);
        }*/
        
        /*const testFormData = new FormData(e.target as HTMLFormElement);
        testFormData.delete('attachments');
        testFormData.delete('receiver_emails');
        testFormData.append('to', formData.receivers);
        testFormData.append('body', formData.body);
        let response = await fetch('http://127.0.0.1:8000/send-email', {
            method: 'POST',
            body: testFormData
        });
        response = await response.json();*/

        let response: OpenMailDataString = await invoke('send_email', formData);
        console.log("Response: ", response);
        /*try{
            let parseResponse = JSON.parse(response) as OpenMailData;
            if(parseResponse.success){
                // Show alert
            }
            sendEmailButton.disabled = false;
            sendEmailButton.textContent = "Send";
        }catch{
            console.error(response);
        }*/
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
            <button type="submit">Send</button>
        </form>
    </div>
</section>
