<script lang="ts">
    import { SharedStore } from '$lib/stores/shared.svelte';
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onMount } from 'svelte';
    import { WYSIWYGEditor } from '@bberkay/wysiwygeditor';
    import { createDomObject, makeSizeHumanReadable, isEmailValid, createSenderAddress, escapeHTML } from '$lib/utils';
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
    const replyTemplate = `
        <br/><br/>
        <div>
            On {original_date}, {original_sender} wrote:<br/>
            <blockquote style="margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex">
                {original_body}
            </blockquote>
        </div>
    `;
    const forwardTemplate = `
        <div>
            ---------- Forwarded message ----------<br/>
            From: {original_sender}<br/>
            Date: {original_date}<br/>
            Subject: {original_subject}<br/>
            To: {original_receiver}<br/>
            <blockquote style=\"margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex\">
                {original_body}
            </blockquote>
        </div>
    `;

    /* Variables */

    interface Props {
        compose_type?: "reply" | "forward";
        original_message_id?: string;
        original_sender?: string;
        original_receiver?: string;
        original_subject?: string;
        original_body?: string;
        original_date?: string;
    }

    let {
        compose_type,
        original_message_id,
        original_sender,
        original_receiver,
        original_subject,
        original_body,
        original_date,
    }: Props = $props();
    let sender: string = $state(createSenderAddress(
        SharedStore.accounts[0].email_address,
        SharedStore.accounts[0].fullname
    ));
    let body: WYSIWYGEditor;
    let attachments: File[] | null = null;
    let subjectInput: HTMLInputElement;
    let composeSenderList: HTMLElement;
    onMount(() => {
        body = new WYSIWYGEditor('body');
        body.init();
        if (compose_type) {
            body.addFullHTMLPage(
                (compose_type == "reply" ? replyTemplate : forwardTemplate)
                    .replace("{original_sender}", escapeHTML((original_sender || "")))
                    .replace("{original_receiver}", escapeHTML((original_receiver || "")))
                    .replace("{original_subject}", original_subject || "")
                    .replace("{original_body}", original_body || "")
                    .replace("{original_date}", original_date || "")
            )
            if (original_subject) {
                subjectInput.value = (compose_type == "reply" ? "Re: " : "Fwd: ") + original_subject
            }
        }
    });

    /* Compose Form Handling Functions */

    const addSender = (email_address: string | null) => {
        if (!email_address) return;
        composeSenderList.style.display = "flex";
        composeSenderList.innerHTML += tagTemplate.replace("{tag}", email_address);
    }

    const addEnteredEmail = (e: Event) => {
        const target = e.target as HTMLInputElement;
        const email_address = target.value.trim();
        const emails = target.closest(".form-group")?.querySelector(".emails") as HTMLElement;

        if (!emails) return;

        if (e instanceof KeyboardEvent && (e.key === " " || e.key === "Spacebar")) {
            e.preventDefault();
            processEmail(target, emails, email_address);
        }
        else if (e instanceof FocusEvent) {
            processEmail(target, emails, email_address);
        }
    };

    function processEmail(target: HTMLInputElement, emails: HTMLElement, email_address: string) {
        if (email_address !== "" && isEmailValid(email_address)) {
            emails.style.display = "flex";
            emails.innerHTML += tagTemplate.replace("{tag}", email_address);
            target.value = "";
        } else if (email_address !== "") {
            target.style.transform = "scale(1.02)";
            setTimeout(() => {
                target.style.transform = "scale(1)";
            }, 100);
        }
    };

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

        formData.set('sender', getEmailAddresses("compose-sender-list"));
        formData.set('body', body.getHTMLContent());
        formData.set('receiver', getEmailAddresses("compose-receiver-list"));
        formData.set('cc', getEmailAddresses("compose-cc-list"));
        formData.set('bcc', getEmailAddresses("compose-bcc-list"));

        if (!formData.get("compose-sender-list")) {
            alert("At least one sender must be added");
        }
        if (!formData.get("compose-receiver-list")) {
            alert("At least one receiver must be added");
        }

        let response;
        if (compose_type !== "reply" && compose_type !== "forward") {
            response = await mailboxController.sendEmail(formData);
        } else if (!original_message_id) {
            alert("original_message_id required when sending reply or forwarding message.");
        } else {
            if (compose_type == "reply") {
                response = await mailboxController.replyEmail(
                    formData,
                    original_message_id
                );
            } else if (compose_type == "forward") {
                response = await mailboxController.forwardEmail(
                    formData,
                    original_message_id
                );
            }
        }

        alert(response!.message);
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
            <Select.Menu onchange={addSender} placeholder="Add sender">
                {#each SharedStore.accounts as account}
                    <Select.Option value={account.email_address}>
                        {account.fullname} &lt;{account.email_address}&gt;
                    </Select.Option>
                {/each}
            </Select.Menu>
             <div class="tags emails" id = "compose-sender-list" bind:this={composeSenderList}></div>
        </div>
        <div class="form-group">
            <label for="receiver">Receiver(s)</label>
            <input type="email" name="receiver" id="receiver" placeholder="someone@domain.xyz" onkeyup={addEnteredEmail} onblur={addEnteredEmail}>
            <div class="tags emails" id = "compose-receiver-list"></div>
        </div>
        <div class="form-group">
            <label for="subject">Subject</label>
            <input type="text" name="subject" id="subject" placeholder="Subject" bind:this={subjectInput} required>
        </div>
        <div class="form-group">
            <label for="cc">Cc</label>
            <input type="email" name="cc" id="cc" placeholder="someone@domain.xyz" onkeyup={addEnteredEmail} onblur={addEnteredEmail}>
            <div class="tags emails" id = "compose-cc-list"></div>
        </div>
        <div class="form-group">
            <label for="bcc">Bcc</label>
            <input type="email" name="bcc" id="bcc" placeholder="someone@domain.xyz" onkeyup={addEnteredEmail} onblur={addEnteredEmail}>
            <div class="tags emails" id = "compose-bcc-list"></div>
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
