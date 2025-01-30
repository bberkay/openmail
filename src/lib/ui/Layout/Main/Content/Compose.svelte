<script lang="ts">
    import { SharedStore } from '$lib/stores/shared.svelte';
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onMount } from 'svelte';
    import { WYSIWYGEditor } from '@bberkay/wysiwygeditor';
    import { createDomObject, makeSizeHumanReadable, isEmailValid } from '$lib/utils';
    import * as Select from "$lib/ui/Elements/Select";
    import Form from "$lib/ui/Elements/Form";
    import { backToDefault } from "$lib/ui/Layout/Main/Content.svelte";

    /* Constants */

    const mailboxController = new MailboxController();
    const fileTemplate = `
        <span class="tag">
            <span class="value">{name}</span>
            <button type="button" style="margin-left:5px;">X</button>
        </span>
    `;
    const tagTemplate = `
        <span class="tag">
            <span class="value">{tag}</span>
            <button type="button" style="margin-left:5px;" onclick="this.parentElement.remove()">X</button>
        </span>
    `;

    /* Variables */

    let sender: string = $state(SharedStore.accounts[0].email_address);
    let body: WYSIWYGEditor;
    let attachments: File[] | null = null;

    onMount(() => {
        body = new WYSIWYGEditor('body');
        body.init();
    });

    /* Compose Form Handling Functions */

    const selectSender = (email_address: string | null) => {
        if (!email_address) return;
        sender = email_address;
    }

    const addEnteredEmail = (e: KeyboardEvent) => {
        const target = e.target as HTMLInputElement;
        const email = target.value;
        const emails = target
            .closest(".form-group")!
            .querySelector(".emails")! as HTMLElement;
        if (e.key === "Spacebar" || e.key === " ") {
            if (email !== "" && isEmailValid(email)) {
                emails.style.display = "flex";
                emails.innerHTML += tagTemplate.replace("{tag}", email);
                target.value = "";
            } else {
                target.style.transform = "scale(1.02)";
                setTimeout(() => {
                    target.style.transform = "scale(1)";
                }, 100);
            }
        }
    }

    const addFile = (e: Event) => {
        const target = e.target as HTMLInputElement;
        attachments = Array.from(target.files as FileList);
        const tags = target.parentElement!.parentElement!.querySelector('.tags')! as HTMLElement;
        Array.from(attachments).forEach((file, index) => {
            const name = `${file.name} (${makeSizeHumanReadable(file.size)})`;
            const fileNode = createDomObject(fileTemplate.replace('{name}', name));
            fileNode!.querySelector('button')!.addEventListener('click', (e: Event) => {
                removeFile(e, index);
            });
            tags.appendChild(fileNode!);
        });
    }

    const removeAllFiles = (e: Event) => {
        const target = e.target as HTMLInputElement;
        const fileInput = target.closest(".form-group")!.querySelector('input') as HTMLInputElement;
        fileInput.value = '';
        attachments = null;
        const tags = target.closest(".form-group")!.querySelector('.tags')! as HTMLElement;
        tags.innerHTML = '';
    }

    const removeFile = (e: Event, index: number) => {
        if(!attachments)
            return;

        const target = e.target as HTMLButtonElement;
        const fileInput = target.closest(".form-group")!.querySelector('input') as HTMLInputElement;
        fileInput.value = '';
        attachments.splice(index, 1);
        target.parentElement?.remove();
    }

    function getEmailAddresses(id: string): string {
        return Array.from(
            document.getElementById(id)!.querySelectorAll("span.value")
        ).map(span => span.textContent).join(',');
    }

    /* Main Operation */

    const sendEmail = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);

        formData.set('sender', sender);
        formData.set('body', body.getHTMLContent());
        formData.set('receiver', getEmailAddresses("added-receivers"));
        formData.set('cc', getEmailAddresses("added-cc"));
        formData.set('bcc', getEmailAddresses("added-bcc"));

        const response = await mailboxController.sendEmail(formData);

        alert(response.message);
        body.clear();
    }
</script>

<div class="header">
    <h2>Compose</h2>
    <button onclick={backToDefault}>X</button>
</div>

<Form onsubmit={sendEmail}>
    <div>
        <div class="form-group">
            <label for="sender">Sender</label>
            <Select.Menu onchange={selectSender} value={SharedStore.accounts[0].email_address}>
                {#each SharedStore.accounts as account}
                    <Select.Option value={account.email_address}>
                        {account.fullname} &lt;{account.email_address}&gt;
                    </Select.Option>
                {/each}
            </Select.Menu>
        </div>
        <div class="form-group">
            <label for="receiver">Receiver(s)</label>
            <input type="email" name="receiver" id="receiver" placeholder="someone@domain.xyz" onkeyup={addEnteredEmail} required>
            <div class="tags emails" id = "added-receivers"></div>
        </div>
        <div class="form-group">
            <label for="subject">Subject</label>
            <input type="text" name="subject" id="subject" placeholder="Subject" required>
        </div>
        <div class="form-group">
            <label for="cc">Cc</label>
            <input type="email" name="cc" id="cc" placeholder="someone@domain.xyz" onkeyup={addEnteredEmail}>
            <div class="tags emails" id = "added-cc"></div>
        </div>
        <div class="form-group">
            <label for="bcc">Bcc</label>
            <input type="email" name="bcc" id="bcc" placeholder="someone@domain.xyz" onkeyup={addEnteredEmail}>
            <div class="tags emails" id = "added-bcc"></div>
        </div>
        <div class="form-group">
            <label for="body">Body</label>
            <div id="body"></div>
        </div>
        <div class="form-group">
            <label for="attachments">Attachment(s)</label>
            <div class="input-group">
                <input type="file" name="attachments" id="attachments" onchange={addFile} multiple>
                <button type="button" onclick={removeAllFiles}>Remove All</button>
            </div>
            <div class="tags"></div>
        </div>
        <button type="submit" id="send-email" style="margin-top:10px;">Send</button>
    </div>
</Form>

<style>
    .header{
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .header :first-child{
        flex-grow:1;
    }
</style>
