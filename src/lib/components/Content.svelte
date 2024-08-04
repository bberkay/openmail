<script lang="ts">
    import type { Email, OpenMailData } from "$lib/types";
    import { onMount } from "svelte";
    import { currentEmail, currentFolder, currentOffset, emails, folders } from "$lib/stores";
    import { get } from "svelte/store";

    const markStatus: {[key: string]: string} = {
        flagged: "Star",
        seen: "Read",
        unflagged: "Remove Star",
        unseen: "Mark as Unread"
    };
    
    let contentBody: HTMLElement;
    let attachments: HTMLElement;
    let markButtons: NodeListOf<HTMLButtonElement>;
    let defaultMarkButtons: NodeListOf<HTMLButtonElement>;    
    onMount(() => {
        contentBody = document.getElementById('body')!;
        attachments = document.getElementById('attachments')!;
        markButtons = document.querySelectorAll('.flag-operations [data-mark-as]');
        defaultMarkButtons = document.querySelectorAll('.flag-operations [data-default-mark]');

        currentEmail.subscribe(value => {
            if(value && Object.keys(value).length > 0)
                getEmailContent(value);
            else
                clearEmailContent();
        });
    });

    function clearEmailContent(){
        (document.querySelector(".email-operations") as HTMLElement).style.display = "none";
        (document.querySelector(".email-content") as HTMLElement).style.display = "none";
        defaultMarkButtons.forEach(button => {
            const mark = button.getAttribute('data-default-mark')!;
            button.innerText = markStatus[mark];
            button.setAttribute('data-mark-as', mark);
        });
        (document.querySelector('select[name="move_to_folder"]') as HTMLSelectElement).selectedIndex = 0;
        contentBody.querySelector("iframe")?.remove();
        contentBody.innerHTML = "";
        attachments.innerHTML = "";
    }

    async function getEmailContent(email: Email): Promise<void>{
        clearEmailContent();
        (document.querySelector(".email-operations") as HTMLElement).style.display = "flex";
        (document.querySelector(".email-content") as HTMLElement).style.display = "block";

        // Body
        if(!email.body)
            return;

        let iframe = document.createElement('iframe');
        contentBody.appendChild(iframe);

        let iframeDoc: Document | null;
        iframeDoc = iframe.contentWindow ? iframe.contentWindow.document : iframe.contentDocument;
        if(iframeDoc){
            iframeDoc.open();
            iframeDoc.writeln(email.body!);
            iframeDoc.close();

            contentBody.style.height = iframeDoc.body.scrollHeight + 'px';
            iframeDoc.body.style.overflow = 'hidden';
        }

        // Flags
        if(Object.hasOwn(email, "flags") && email["flags"].length > 0){
            email["flags"].forEach(flag => {
                flag = flag.toLowerCase();
                if(Object.hasOwn(markStatus, flag)){
                    const markButton = document.querySelector('[data-default-mark="' + flag + '"]') as HTMLButtonElement;
                    flag = "un" + flag;
                    markButton.innerText = markStatus[flag];
                    markButton.setAttribute('data-mark-as', flag);
                }
            });
        }
        
        // Attachment
        if(Object.hasOwn(email, "attachments")){
            email["attachments"]!.forEach(attachment => {
                const decodedData = atob(attachment.data);
                const byteNumbers = Array.from(decodedData, char => char.charCodeAt(0));
                const link = document.createElement('a');
                link.classList.add('attachment');
                link.href = URL.createObjectURL(new Blob([new Uint8Array(byteNumbers)], {type: attachment.type}));
                link.download = attachment.name;
                link.innerText = attachment.name + " (" + attachment.size + ")";
                attachments.appendChild(link);
            });
        }
    }

    async function markEmail(event: Event): Promise<void>{
        const mark = (event.target as HTMLButtonElement).getAttribute('data-mark-as')!;
        const response: OpenMailData = await fetch('http://127.0.0.1:8000/mark-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ uid: get(currentEmail).uid, mark: mark, folder: get(currentFolder) })
        }).then(res => res.json());
        if(response.success){
            currentEmail.update(value => {
                if(value && Object.keys(value).length > 0){
                    if(mark.startsWith("un"))
                        value.flags = value.flags.filter(flag => flag.toLowerCase() != mark.slice(2));
                    else
                        value.flags.push(mark.slice(0, 1).toUpperCase() + mark.slice(1).toLowerCase());

                    return value;
                }
                return value;
            })
        }
    }

    async function moveEmail(event: Event): Promise<void>{
        const folder = (event.target as HTMLSelectElement).value;
        const response: OpenMailData = await fetch('http://127.0.0.1:8000/move-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ uid: get(currentEmail).uid, source: get(currentFolder), destination: folder })
        }).then(res => res.json());
        if(response.success){
            emails.update(value => value.filter(email => email.uid != get(currentEmail).uid));
            currentEmail.set({} as Email);
            currentOffset.update(value => value - 1);
        }
    }
</script>

<section class="card">
    <div class="email-header">
        <h2>Email</h2>
        <hr>
        <div class="email-operations">
            <div class="flag-operations">
                <button data-mark-as="seen" data-default-mark="seen" on:click={markEmail}>Read</button>
                <button data-mark-as="flagged" data-default-mark="flagged" on:click={markEmail}>Star</button>
                <select name="move_to_folder" on:change={moveEmail}>
                    <option value="">Move To Folder</option>
                    {#if $folders && $folders.length > 0}
                        {#each $folders as folder}
                            <option value={folder}>{folder}</option>
                        {/each}
                    {/if}
                </select>
                <button>Delete</button>
            </div>
            <div class="answer-operations">
                <button>Reply</button>
                <button>Forward</button>
            </div>
        </div>
    </div>
    <div class="email-content">
        <div class="tags">
            <span>{$currentEmail.flags}</span>
            <!--{#if $currentEmail.flags && $currentEmail.flags.length > 0}
                {#each get(currentEmail).flags as flag}
                    <span class="flag">{flag}</span>
                {/each}
            {/if}-->
        </div>
        <div id="subject">
            <h3>{$currentEmail.subject || ""}</h3>
            <p>From: {$currentEmail.from || ""}</p>
            <p>To: {$currentEmail.to || ""}</p>
            <p>Date: {$currentEmail.date || ""}</p>
        </div>
        <div id="body"></div>
        <div id="attachments"></div>
    </div>
</section>

<style>
    .email-operations, .email-content{
        display:none;
    }

    .email-operations{
        justify-content:space-between;
        align-items: center;

        & .flag-operations, & .answer-operations{
            display: flex;
            align-items: center;
        }
    }

    .email-content{
        width: 100%;
        border-top:2px solid #3a3a3a;
        margin-top: 0.5rem;
        
        & iframe{
            border: none;
            width: 100%;
            height: 100%;
        }

        & .tags {
            display: flex;
            margin-top:10px;

            & button{
                display: none;
            }
        }

        & #attachments{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;

            & a.attachment{
                padding: 0.5rem;
                background-color: #f8f3c7;
                color: #121212;
                text-decoration: none;
                border-radius: 0.5rem;
                transition: background-color 0.2s;

                &:hover{
                    background-color: #f8f4d4;
                }
            }
        }
    }
</style>