<script lang="ts">
    import { onMount } from 'svelte';
    import { WYSIWYGEditor } from '@bberkay/wysiwygeditor';
    import { SharedStore } from '$lib/stores/shared.svelte';
    import { createDomObject, makeSizeHumanReadable } from '$lib/utils';
    import Select from "$lib/components/Elements/Select.svelte";
    import Form from "$lib/components/Elements/Form.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";

    const mailboxController = new MailboxController();

    let sender: string = $state(SharedStore.accounts[0].email_address);
    let body: WYSIWYGEditor;
    let attachments: File[] | null = null;
    const fileTagTemplate = `
        <span class="tag">
            <span class="value">{name}</span>
            <button type="button" style="margin-left:5px;">X</button>
        </span>
    `;

    interface Props {
        showInbox: () => void
    }

    let { showInbox }: Props = $props();
    onMount(() => {
        body = new WYSIWYGEditor('body');
        body.init();
    });

    const handleTagEnter = (e: KeyboardEvent) => {
        const target = e.target as HTMLInputElement;
        const tags = target.closest(".form-group")!.querySelector('.tags')! as HTMLElement;
        const isEmailValid = target.value.match(/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/);
        if((e.key === 'Spacebar' || e.key === ' ')){
            if(target.value !== '' && isEmailValid){
                tags.style.display = 'flex';
                tags.innerHTML += `<span class="tag"><span class="value">${target.value}</span><button type="button" style="margin-left:5px;" onclick="this.parentElement.remove()">X</button></span>`;
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

    const handleFileUpload = (e: Event) => {
        const target = e.target as HTMLInputElement;
        attachments = Array.from(target.files as FileList);
        const tags = target.parentElement!.parentElement!.querySelector('.tags')! as HTMLElement;
        Array.from(attachments).forEach((file, index) => {
            const name = `${file.name} (${makeSizeHumanReadable(file.size)})`;
            const fileNode = createDomObject(fileTagTemplate.replace('{name}', name));
            fileNode!.querySelector('button')!.addEventListener('click', (e) => {
                removeFile(e, index);
            });
            tags.appendChild(fileNode!);
        });
    }

    const clearAllFiles = (e: Event) => {
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

    const getTagValues = (id: string): string => {
        return Array.from(
            document.getElementById(id)!.querySelectorAll("span.value")
        ).map(span => span.textContent).join(',');
    }

    const sendEmail = async (form: HTMLFormElement): Promise<void> => {
        const formData = new FormData(form);

        formData.set('sender', sender);
        formData.set('body', body.getHTMLContent());
        formData.set('receiver', getTagValues("saved-receivers"));
        formData.set('cc', getTagValues("saved-cc"));
        formData.set('bcc', getTagValues("saved-bcc"));

        const response = await mailboxController.sendEmail(formData);

        alert(response.message);
        body.clear();
    }

    const selectSender = (email_address: string | null) => {
        if (!email_address) return;
        sender = email_address;
    }
</script>

<div class="header">
    <h2>Compose</h2>
    <button onclick={showInbox}>X</button>
</div>

<Form Inner={ComposeForm} operation={sendEmail} />

{#snippet ComposeForm()}
    <div>
        <div class="form-group">
            <label for="sender">Sender</label>
            <Select
                id="sender"
                options={SharedStore.accounts.map((account, index) => ({ value: account.email_address, inner: `${account.fullname} &lt;${account.email_address}&gt;` }))}
                operation={selectSender}
                placeholder={{ value: SharedStore.accounts[0].email_address, inner: `${SharedStore.accounts[0].fullname} &lt;${SharedStore.accounts[0].email_address}&gt;` }}
            />
        </div>
        <div class="form-group">
            <label for="receiver">Receiver(s)</label>
            <input type="email" name="receiver" id="receiver" placeholder="someone@domain.xyz" onkeyup={handleTagEnter} required>
            <div class="tags" id = "saved-receivers"></div>
        </div>
        <div class="form-group">
            <label for="subject">Subject</label>
            <input type="text" name="subject" id="subject" placeholder="Subject" required>
            <div class="tags"></div>
        </div>
        <div class="form-group">
            <label for="cc">Cc</label>
            <input type="email" name="cc" id="cc" placeholder="someone@domain.xyz" onkeyup={handleTagEnter}>
            <div class="tags" id = "saved-cc"></div>
        </div>
        <div class="form-group">
            <label for="bcc">Bcc</label>
            <input type="email" name="bcc" id="bcc" placeholder="someone@domain.xyz" onkeyup={handleTagEnter}>
            <div class="tags" id = "saved-bcc"></div>
        </div>
        <div class="form-group">
            <label for="body">Body</label>
            <div id="body"></div>
        </div>
        <div class="form-group">
            <label for="attachments">Attachment(s)</label>
            <div class="input-group">
                <input type="file" name="attachments" id="attachments" onchange={handleFileUpload} multiple>
                <button type="button" onclick={clearAllFiles}>Clear</button>
            </div>
            <div class="tags"></div>
        </div>
        <button type="submit" id="send-email" style="margin-top:10px;">Send</button>
    </div>
{/snippet}

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
