<script lang="ts">
    import { onMount } from 'svelte';
    import { mount, unmount } from "svelte";
    import { WYSIWYGEditor } from '@bberkay/wysiwygeditor';
    import { SharedStore } from '$lib/stores/shared.svelte';
    import Loader from "$lib/components/Loader.svelte";
    import { ApiService } from '$lib/services/ApiService';
    import { PostRoutes } from '$lib/services/ApiService';
    import { createDomObject, makeSizeHumanReadable } from '$lib/utils';

    let body: WYSIWYGEditor;
    let attachments: File[] | null = null;
    const fileTagTemplate = `
        <span class="tag">
            <span class="value">{name}</span>
            <button type="button" style="margin-left:5px;">X</button>
        </span>
    `;
    onMount(() => {
        body = new WYSIWYGEditor('body');
        body.init();
    });

    function handleTagEnter(e: KeyboardEvent){
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

    function handleFileUpload(e: Event){
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

    function clearAllFiles(e: Event) {
        const target = e.target as HTMLInputElement;
        const fileInput = target.closest(".form-group")!.querySelector('input') as HTMLInputElement;
        fileInput.value = '';
        attachments = null;
        const tags = target.closest(".form-group")!.querySelector('.tags')! as HTMLElement;
        tags.innerHTML = '';
    }

    function removeFile(e: Event, index: number) {
        if(!attachments)
            return;

        const target = e.target as HTMLButtonElement;
        const fileInput = target.closest(".form-group")!.querySelector('input') as HTMLInputElement;
        fileInput.value = '';
        attachments.splice(index, 1);
        target.parentElement?.remove();
    }

    function getTagValues(id: string): string {
        return Array.from(
            document.getElementById(id)!.querySelectorAll("span.value")
        ).map(span => span.textContent).join(',');
    }

    async function handleSendEmail(e: Event) {
        e.preventDefault();

        const eventButton = (e.target as HTMLButtonElement).querySelector('button[type="submit"]') as HTMLButtonElement;
        eventButton.disabled = true;
        const temp = eventButton.innerText;
        eventButton.innerText = "";
        const loader = mount(Loader, { target: eventButton });

        const formData = new FormData(e.target as HTMLFormElement);

        formData.delete('receiver');
        formData.set('receiver', getTagValues("saved-receivers"));

        formData.delete('cc');
        formData.set('cc', getTagValues("saved-cc"));

        formData.delete('bcc');
        formData.set('bcc', getTagValues("saved-bcc"));

        formData.set('body', body.getHTMLContent());

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.SEND_EMAIL,
            formData
        );

        alert(response.message);
        (e.target as HTMLFormElement).reset();
        body.clear();

        eventButton.disabled = false;
        eventButton.innerText = temp;
        unmount(loader);
    }
</script>

<div class = "card">
    <h2>Compose</h2>
    <form onsubmit={handleSendEmail}>
        <div class="form-group">
            <label for="sender">Sender</label>
            <select name="sender" id="sender" required>
                {#each SharedStore.accounts as account}
                    <option value={account.email_address}>{account.fullname} &lt;{account.email_address}&gt;</option>
                {/each}
            </select>
        </div>
        <div class="form-group">
            <label for="receiver">Receiver(s)</label>
            <input type="email" name="receiver" id="receiver" onkeyup={handleTagEnter} required>
            <div class="tags" id = "saved-receivers"></div>
        </div>
        <div class="form-group">
            <label for="subject">Subject</label>
            <input type="text" name="subject" id="subject" required>
            <div class="tags"></div>
        </div>
        <div class="form-group">
            <label for="cc">Cc</label>
            <input type="email" name="cc" id="cc" onkeyup={handleTagEnter}>
            <div class="tags" id = "saved-cc"></div>
        </div>
        <div class="form-group">
            <label for="bcc">Bcc</label>
            <input type="email" name="bcc" id="bcc" onkeyup={handleTagEnter}>
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
    </form>
</div>
