<script lang="ts">
    import type { OpenMailDataString } from "$lib/types";
    import { invoke } from "@tauri-apps/api/core";
    import { clickedEmailId } from "$lib/stores";
    import { onMount } from "svelte";

    let email: {
        id: string,
        from: string,
        to: string,
        subject: string,
        body: string,
        date: string,
        flags: string
    } = {
        id: "",
        from: "",
        to: "",
        subject: "",
        body: "",
        date: "",
        flags: ""
    };

    clickedEmailId.subscribe(value => {
        if(value)
            getEmailContent(value);
    });

    let contentBody: HTMLElement;
    let attachments: HTMLElement;
    let flags: HTMLElement;
    onMount(() => {
        contentBody = document.getElementById('body')!;
        attachments = document.getElementById('attachments')!;
        flags = document.querySelector('.tags')!;
        contentBody.innerHTML = "";
        attachments.innerHTML = "";
        flags.innerHTML = "";
    });

    async function getEmailContent(email_id: string){
        let response: OpenMailDataString = await invoke('get_email_content', { id: email_id });
        response = JSON.parse(response);
        if(response["success"] === true)
            email = response["data"];
        
        // Flags
        email["flags"].forEach(flag => {
            console.log(flag);
            const flagElement = document.createElement('span');
            flagElement.classList.add('flag');
            flagElement.innerText = flag;
            flags.appendChild(flagElement)
            /*flag = flag.trim().toLowerCase();
            const markButton = document.querySelector(`[data-mark-as="${flag}"]`);
            if(!markButton) return
            markButton.setAttribute("data-mark-as", "un" + flag);
            markButton.innerText = markButtonTextMap[flag];*/
        });

        // Body
        let iframe = document.createElement('iframe');
        contentBody.appendChild(iframe);
        iframe = iframe.contentWindow ? iframe.contentWindow.document : (iframe.document || iframe.contentDocument);
        iframe.open();
        iframe.writeln(email.body);
        iframe.close();
        contentBody.style.height = iframe.body.scrollHeight + 'px';
        iframe.body.style.overflow = 'hidden';

        // Attachment
        email["attachments"].forEach(attachment => {
            const decodedData = atob(attachment["data"]);
            const byteNumbers = new Array(decodedData.length);
            for(let i=0; i<decodedData.length; i++){
                byteNumbers[i] = decodedData.charCodeAt(i);
            }
            const link = document.createElement('a');
            link.classList.add('attachment');
            link.href = URL.createObjectURL(new Blob([new Uint8Array(byteNumbers)], {type: attachment["type"]}));
            link.download = attachment["name"];
            link.innerText = attachment["name"];
            attachments.appendChild(link);
        });
    }
</script>

<section class="card">
    <div class="email-header">
        <h2>Email</h2>
        <hr>
        <div class="email-operations">
            <div class="flag-operations">
                <button>Read</button>
                <button>Star</button>
                <select>
                    <option value="">Move To Folder</option>
                </select>
                <button>Delete</button>
            </div>
            <div class="answer-operations">
                <button>Reply</button>
                <button>Forward</button>
            </div>
        </div>
    </div>
    <hr>
    <div class="email-content">
        <div class="tags">
            <!-- Flags -->
        </div>
        <div id="subject">
            <h3>{email.subject}</h3>
            <p>From: {email.from}</p>
            <p>To: {email.to}</p>
            <p>Date: {email.date}</p>
        </div>
        <div id="body"></div>
        <div id="attachments"></div>
    </div>
</section>

<style>
    .email-operations{
        display: flex;
        justify-content:space-between;
        align-items: center;

        & .flag-operations, & .answer-operations{
            display: flex;
            align-items: center;
        }
    }

    .email-content{
        width: 100%;
        max-height: 85vh;
        overflow-y: auto;
        overflow-x: hidden;
        
        & iframe{
            border: none;
            width: 100%;
            height: 100%;
        }

        & .tags {
            & button{
                display: none;
            }
        }
    }
</style>