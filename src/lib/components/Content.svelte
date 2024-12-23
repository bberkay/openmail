<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { Attachment, EmailWithContent } from "$lib/types";
    import { onMount } from "svelte";

    let contentBody: HTMLElement;
    let attachments: HTMLElement;
    onMount(() => {
        contentBody = document.getElementById("body")!;
        attachments = document.getElementById("attachments")!;
    })

    $effect(() => {
        if(SharedStore.shownEmail) {
            contentBody.innerHTML = "";
            attachments.innerHTML = "";
            printEmailContent(SharedStore.shownEmail);
        }
    })

    function printEmailContent(email: EmailWithContent): void {
        if (!email.body) return;

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
            iframeDoc.body.style.overflow = "hidden";
        }

        // Attachment
        if (Object.hasOwn(email, "attachments")) {
            email["attachments"]!.forEach((attachment: Attachment) => {
                const decodedData = atob(attachment.data);
                const byteNumbers = Array.from(decodedData, (char) =>
                    char.charCodeAt(0),
                );
                const link = document.createElement("a");
                link.classList.add("attachment");
                link.href = URL.createObjectURL(
                    new Blob([new Uint8Array(byteNumbers)], {
                        type: attachment.type,
                    }),
                );
                link.download = attachment.name;
                link.innerText = attachment.name + " (" + attachment.size + ")";
                attachments.appendChild(link);
            });
        }
    }

    async function markEmail(event: Event): Promise<void> {
    }

    async function moveEmail(event: Event): Promise<void> {
    }

    async function deleteEmail(event: Event): Promise<void> {
    }
</script>

<div class = "card" style="width:55%;margin-left:5px;">
    {#if SharedStore.shownEmail}
        <div id="subject" style="margin-bottom: 5px;">
            <h3>{SharedStore.shownEmail.subject || ""}</h3>
            <p>From: {SharedStore.shownEmail.receiver || ""}</p>
            <p>To: {SharedStore.shownEmail.sender || ""}</p>
            <p>Date: {SharedStore.shownEmail.date || ""}</p>
            {#if Object.hasOwn(SharedStore.shownEmail, "flags") && SharedStore.shownEmail.flags}
                {#each SharedStore.shownEmail.flags as flag}
                    <span class = "tag">{flag}</span>
                {/each}
            {/if}
        </div>
        <div id="body"></div>
        <div id="attachments"></div>
    {/if}
</div>
