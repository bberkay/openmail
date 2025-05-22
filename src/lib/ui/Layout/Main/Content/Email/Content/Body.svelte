<script lang="ts">
    import { onMount } from "svelte";
    import { type Email } from "$lib/types";

    interface Props {
        email: Email;
    }

    let { email }: Props = $props();

    let body: HTMLElement;
    onMount(() => {
        renderBody();
    });

    function renderBody(): void {
        body.innerHTML = "";

        let iframe = document.createElement("iframe");
        body.appendChild(iframe);

        let iframeDoc: Document | null;
        iframeDoc = iframe.contentWindow
            ? iframe.contentWindow.document
            : iframe.contentDocument;
        if (iframeDoc) {
            iframeDoc.open();
            iframeDoc.writeln(email.body);
            iframeDoc.close();

            body.style.height = iframeDoc.body.scrollHeight + "px";
        }
    }
</script>

<div class="body" bind:this={body}></div>
