<script lang="ts">
    import { SharedStore } from '$lib/stores/shared.svelte';
    import { REPLY_TEMPLATE, FORWARD_TEMPLATE } from '$lib/constants';
    import { Folder } from '$lib/types';
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onMount } from 'svelte';
    import { WYSIWYGEditor } from '@bberkay/wysiwygeditor';
    import { isEmailValid, createSenderAddress, extractEmailAddress, escapeHTML, pulseTarget } from '$lib/utils';
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import Collapse from "$lib/ui/Components/Collapse";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Badge from "$lib/ui/Components/Badge";
    import Inbox from "$lib/ui/Layout/Main/Content/Inbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    /* Constants */

    const mailboxController = new MailboxController();

    /* Variables */

    interface Props {
        compose_type?: "reply" | "forward";
        original_message_id?: string;
        original_sender?: string;
        original_receivers?: string;
        original_subject?: string;
        original_body?: string;
        original_date?: string;
    }

    let {
        compose_type,
        original_message_id,
        original_sender,
        original_receivers,
        original_subject,
        original_body,
        original_date,
    }: Props = $props();

    let body: WYSIWYGEditor;
    let senders: string[] = $state([]);
    let receivers: string[] = $state([]);
    let cc: string[] = $state([]);
    let bcc: string[] = $state([]);

    onMount(() => {
        body = new WYSIWYGEditor('body');
        body.init();
        if (compose_type) {
            body.addFullHTMLPage(
                (compose_type == "reply" ? REPLY_TEMPLATE : FORWARD_TEMPLATE)
                    .replace("{original_sender}", escapeHTML((original_sender || "")))
                    .replace("{original_receivers}", escapeHTML((original_receivers || "")))
                    .replace("{original_subject}", original_subject || "")
                    .replace("{original_body}", original_body || "")
                    .replace("{original_date}", original_date || "")
            )
        }
    });

    /* Form Handling Functions */

    const addAddress = (address: string, addressList: string[]) => {
        addressList.push(address);
    }

    const removeAddress = (address: string, addressList: string[]) => {
        addressList = addressList.filter(addr => addr !== address);
    }

    const addEnteredAddress = (e: Event, addressList: string[]) => {
        const target = e.target as HTMLInputElement;
        const emails = target.closest(".form-group")!.querySelector(".tags") as HTMLElement;
        if (!emails)
            return;

        const address = target.value.trim();
        if (address == "")
            return;

        if (e instanceof KeyboardEvent && (e.key === " " || e.key === "Spacebar")) {
            e.preventDefault();
        } else if (!(e instanceof FocusEvent)) {
            return;
        }

        if (!isEmailValid(extractEmailAddress(address))) {
            pulseTarget(target);
            return;
        }

        addAddress(address, addressList);
        target.value = "";
    };

    /* Main Operation */

    const sendEmail = async (e: Event): Promise<void> => {
        if (
            (compose_type == "reply" || compose_type == "forward") &&
            !original_message_id
        ) {
            showMessage({content: "Unexpected error while replying/forwarding."});
            console.error("`original_message_id` required when sending reply or forwarding message.");
            return;
        }

        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);

        formData.set('sender', senders.join(","));
        formData.set('receivers', receivers.join(","));

        if (!formData.get("sender")) {
            showMessage({content: "At least one sender must be added"});
            console.error("At least one sender must be added");
            return;
        }
        if (!formData.get("receivers")) {
            showMessage({content: "At least one receiver must be added"});
            console.error("At least one receiver must be added");
            return;
        }

        formData.set('cc', cc.join(","));
        formData.set('bcc', bcc.join(","));
        formData.set('body', body.getHTMLContent());

        let response;
        if (compose_type == "reply") {
            response = await mailboxController.replyEmail(
                formData,
                original_message_id!
            );
        } else if (compose_type == "forward") {
           response = await mailboxController.forwardEmail(
               formData,
               original_message_id!
           );
        } else {
            response = await mailboxController.sendEmail(formData);
        }

        if (!response.success) {
            showMessage({content: "Unexpected error while replying/forwarding."});
            console.error(response!.message);
            return;
        }

        body.clear();

        // Set current folder to Folder.Sent and
        // mount Inbox.
        const firstSenderIndex = SharedStore.standardFolders.findIndex(
            account => account.email_address === senders[0]
        );
        SharedStore.currentFolder = SharedStore.standardFolders[firstSenderIndex].result.filter(
            (folder: string) => folder.toLowerCase().includes(Folder.Sent.toLowerCase())
        )[0];
        showContent(Inbox);
    }
</script>

<div class="compose">
    <Form onsubmit={sendEmail}>
        <div>
            <FormGroup>
                <Label for="senders">Sender(s)</Label>
                <Select.Root onchange={(addr) => addAddress(addr, senders)} placeholder="Add sender">
                    {#each SharedStore.accounts as account}
                        {@const sender = createSenderAddress(account.email_address, account.fullname)}
                        <Select.Option value={sender}>
                            {sender}
                        </Select.Option>
                    {/each}
                </Select.Root>
                <div class="tags">
                    {#each senders as sender}
                        <Badge
                            content={sender}
                            onclick={() => removeAddress(sender, senders)}
                        />
                    {/each}
                </div>
            </FormGroup>
            <FormGroup>
                <Label for="receivers">Receiver(s)</Label>
                <Input.Basic
                    type="email"
                    name="receivers"
                    id="receivers"
                    placeholder="someone@domain.xyz"
                    onkeyup={(e: Event) => addEnteredAddress(e, receivers)}
                    onblur={(e: Event) => addEnteredAddress(e, receivers)}
                />
                <div class="tags">
                    {#each receivers as receiver}
                        <Badge
                            content={receiver}
                            onclick={() => removeAddress(receiver, receivers)}
                        />
                    {/each}
                </div>
            </FormGroup>
            <FormGroup>
                <Label for="subject">Subject</Label>
                <Input.Basic
                    type="text"
                    name="subject"
                    id="subject"
                    placeholder="Subject"
                    value={
                        compose_type && original_subject
                            ? (compose_type == "reply" ? "Re: " : "Fwd: ") + original_subject
                            : ""
                    }
                    required
                />
            </FormGroup>
            <FormGroup>
                <Collapse title="Cc">
                    <Label for="cc">Cc</Label>
                    <Input.Basic
                        type="email"
                        name="cc"
                        id="cc"
                        placeholder="someone@domain.xyz"
                        onkeyup={addEnteredAddress}
                        onblur={addEnteredAddress}
                    />
                </Collapse>
                <div class="tags">
                    {#each cc as ccAddr}
                        <Badge
                            content={ccAddr}
                            onclick={() => removeAddress(ccAddr, cc)}
                        />
                    {/each}
                </div>
            </FormGroup>
            <FormGroup>
                <Collapse title="Bcc">
                    <Label for="bcc">Bcc</Label>
                    <Input.Basic
                        type="email"
                        name="bcc"
                        id="bcc"
                        placeholder="someone@domain.xyz"
                        onkeyup={addEnteredAddress}
                        onblur={addEnteredAddress}
                        />
                </Collapse>
                <div class="tags">
                    {#each bcc as bccAddr}
                        <Badge
                            content={bccAddr}
                            onclick={() => removeAddress(bccAddr, bcc)}
                        />
                    {/each}
                </div>
            </FormGroup>
            <FormGroup>
                <Label for="body">Body</Label>
                <div id="body"></div>
            </FormGroup>
            <FormGroup>
                <Label for="attachments">Attachment(s)</Label>
                <Input.File
                    name="attachments"
                    id="attachments"
                    multiple
                />
            </FormGroup>
            <Button.Basic
                type="submit"
                id="send-email"
                style="margin-top:10px"
                onclick={() => {}}
            >
                Send Email
            </Button.Basic>
        </div>
    </Form>
</div>

<style>
    .compose {
        display: flex;
        flex-direction: column;
        padding: var(--spacing-lg);
        border: 1px solid var(--color-border-subtle);
        border-radius: var(--radius-sm);

        & .tags {
            margin-top: var(--spacing-2xs);
            font-size: var(--font-size-sm);
        }
    }
</style>
