<script lang="ts">
    import { onMount } from 'svelte';
    import { accounts, serverUrl } from '$lib/stores';
    import type { Response, Account } from '$lib/types';
    import { get } from "svelte/store";

    // @ts-ignore
    let body: WYSIWYGEditor;
    let receivers: HTMLElement;
    let sendEmailButton: HTMLButtonElement;
    let selectedAccount: Account = get(accounts)[0];
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

    async function handleSendEmail(e: Event) {
        sendEmailButton.disabled = true;
        sendEmailButton.textContent = 'Sending...';

        const formData = new FormData(e.target as HTMLFormElement);
        formData.set('receivers', Array.from(document.getElementById('receivers')!.parentElement!.querySelectorAll(".tags span")).map(span => span.textContent).join(','));
        formData.set('body', body.getHTMLContent());

        const response: Response = await fetch(`${get(serverUrl)}/send-email`, {
            method: 'POST',
            body: formData
        }).then(res => res.json());

        if (response.success) {
            sendEmailButton.textContent = 'Send';
            sendEmailButton.disabled = false;
        }
    }

    function setSelectedAccount(e: Event){
        const target = e.target as HTMLSelectElement;
        selectedAccount = get(accounts).find(account => account.email === target.value)!;
    }
</script>

<section class="send-email">
    <div class="card">
        <form id="send-email-form" on:submit|preventDefault={handleSendEmail}>
            <div class="form-group">
                <label for="sender_name">Fullname (Optional)</label>
                <input type="text" name="sender_name" id="sender_name" bind:value={selectedAccount.fullname}>
                <small style="margin-top:2px;font-style:italic;">{selectedAccount.fullname} &lt;{selectedAccount.email}&gt;</small>
            </div>
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <select name="email_address" id="email_address" on:change={setSelectedAccount}>
                    {#each $accounts as currentAccount}
                        <option value={currentAccount.email} selected>{currentAccount.email}</option>
                    {/each}
                </select>
            </div>
            <div class="form-group">
                <label for="receivers">Receiver(s)</label>
                <input type="email" name="receivers" id="receivers" on:keyup={handleReceivers}>
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
            </div>-
            <button type="submit">Send</button>
        </form>
    </div>
</section>
