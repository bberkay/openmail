<script lang="ts">
    import type { Email } from "$lib/types";
    import { onMount } from "svelte";
    import { currentEmail, folders } from "$lib/stores";
    
    let folderSelectOptions: NodeListOf<HTMLFormElement>;
    let contentBody: HTMLElement;
    let attachments: HTMLElement;
    let flags: HTMLElement;
    onMount(() => {
        contentBody = document.getElementById('body')!;
        attachments = document.getElementById('attachments')!;
        flags = document.querySelector('.email-content .tags')!;
        contentBody.innerHTML = "";
        attachments.innerHTML = "";
        flags.innerHTML = "";

        currentEmail.subscribe(value => {
            if(value && Object.keys(value).length > 0)
                getEmailContent(value);
        });

        folderSelectOptions = document.querySelectorAll('.flag-operations select[name*="folder"]');
        folders.subscribe(value => {
            if(value.length > 0){
                folderSelectOptions.forEach(select => {
                    value.forEach(folder => {
                        const option = document.createElement('option');
                        option.value = folder;
                        option.innerText = folder;
                        select.appendChild(option);
                    });
                });
            }
        })
    });

    async function getEmailContent(email: Email){
        (document.querySelector(".email-operations") as HTMLElement).style.display = "flex";
        (document.querySelector(".email-content") as HTMLElement).style.display = "block";
        contentBody.innerHTML = "";
        attachments.innerHTML = "";
        flags.innerHTML = "";
    
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
            flags.style.display = "flex";
            email["flags"].forEach(flag => {
                const flagElement = document.createElement('span');
                flagElement.classList.add('flag');
                flagElement.innerText = flag;
                flags.appendChild(flagElement)
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
    <div class="email-content">
        <div class="tags">
            <!-- Flags -->
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
        border-top:3px solid #3a3a3a;
        
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