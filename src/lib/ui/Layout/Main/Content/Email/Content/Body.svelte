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
            iframe.onload = () => {
                const iframeBody = iframe.contentDocument?.body;
                if (iframeBody) {
                    const height = iframeBody.scrollHeight;
                    body.style.height = `${height}px`;
                }
            };
        }
    }
</script>

<div class="body" bind:this={body}></div>

<style>
    .body {
        :global(iframe) {
            display: block;
            width: 100%;
            height: 100%;
            border: none;
            background-color: white;
        }
    }
</style>
