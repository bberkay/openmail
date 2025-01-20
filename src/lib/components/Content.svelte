<script lang="ts">
    import { mount, unmount } from "svelte";
    import Loader from "$lib/components/Elements/Loader.svelte";
    import { create, BaseDirectory } from '@tauri-apps/plugin-fs';
    import type { Attachment, EmailWithContent } from "$lib/types";
    import { onMount } from "svelte";
    import { makeSizeHumanReadable } from "$lib/utils";

    let { email }: { email: EmailWithContent } = $props();

    let contentBody: HTMLElement;
    let attachments: HTMLElement;

    $effect(() => {
        printEmailContent(email);
    });

    function printEmailContent(email: EmailWithContent): void {
        contentBody.innerHTML = "";
        attachments.innerHTML = "";

        // Body
        let iframe = document.createElement("iframe");
        contentBody.appendChild(iframe);

        let iframeDoc: Document | null;
        iframeDoc = iframe.contentWindow
            ? iframe.contentWindow.document
            : iframe.contentDocument;
        if (iframeDoc) {
            iframeDoc.open();
            iframeDoc.writeln(email.body!);
            iframeDoc.close();

            contentBody.style.height = iframeDoc.body.scrollHeight + "px";
        }

        // Attachment
        if (Object.hasOwn(email, "attachments")) {
            email.attachments!.forEach((attachment: Attachment, index: number) => {
                const link = document.createElement("a");
                link.classList.add("attachment");
                link.id = "attachment-" + index;
                link.href = "#";
                link.onclick = async () => { downloadFile(link.id, attachment) }
                link.download = attachment.name;
                link.innerText = attachment.name + " (" + makeSizeHumanReadable(parseInt(attachment.size)) + ")";
                attachments.appendChild(link);
            });
        }
    }

    async function downloadFile(linkId: string, attachment: Attachment): Promise<void> {
        const link = document.getElementById(linkId)!;
        const tempInnerHTML = link.innerHTML;
        link.innerHTML = "";
        const loader = mount(Loader, { target: link });

        const file = await create(attachment.name, { baseDir: BaseDirectory.Download });
        await file.write(Uint8Array.from(atob(attachment.data), (char) => char.charCodeAt(0)));
        await file.close();

        unmount(loader);
        link.innerHTML = tempInnerHTML;
    }
</script>

<div id="subject" style="margin-bottom: 5px;">
    <h3>{email.subject || ""}</h3>
    <p>From: {email.receiver || ""}</p>
    <p>To: {email.sender || ""}</p>
    <p>Date: {email.date || ""}</p>
    {#if Object.hasOwn(email, "flags") && email.flags}
        {#each email.flags as flag}
            <span class = "tag">{flag}</span>
        {/each}
    {/if}
</div>
<div id="body" bind:this={contentBody}></div>
<div id="attachments" bind:this={attachments}></div>

<style>
    #body:not(:has(iframe)) {
        background-color: #f5f5f5;
        color: #333;
        padding: 10px;
        overflow-y: scroll;
        overflow-x: hidden;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #ccc;
        border-radius: 5px;
    }

    #attachments {
        margin-top: 1.5rem;
    }
</style>
