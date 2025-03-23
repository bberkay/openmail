<script lang="ts">
    import { SharedStore } from '$lib/stores/shared.svelte';
    import { REPLY_TEMPLATE, FORWARD_TEMPLATE } from '$lib/constants';
    import { Folder } from '$lib/types';
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onMount } from 'svelte';
    import { WYSIWYGEditor } from '@bberkay/wysiwygeditor';
    import { createSenderAddress, escapeHTML, addEmailToAddressList } from '$lib/utils';
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import Icon from "$lib/ui/Components/Icon";
    import Collapse from "$lib/ui/Components/Collapse";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Badge from "$lib/ui/Components/Badge";
    import Inbox from "$lib/ui/Layout/Main/Content/Inbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

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

    const addReceiver = (e: Event) => {
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>('input[id="receivers"]')!;
        addEmailToAddressList(e, targetInput, cc);
    }

    const addCc = (e: Event) => {
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>('input[id="cc"]')!;
        addEmailToAddressList(e, targetInput, bcc);
    }

    const addBcc = (e: Event) => {
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>('input[id="bcc"]')!;
        addEmailToAddressList(e, targetInput, bcc);
    }

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
            response = await MailboxController.replyEmail(
                formData,
                original_message_id!
            );
        } else if (compose_type == "forward") {
           response = await MailboxController.forwardEmail(
               formData,
               original_message_id!
           );
        } else {
            response = await MailboxController.sendEmail(formData);
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
                <Select.Root
                    id="senders"
                    placeholder="Add sender"
                    onchange={(addr) => senders.push(addr)}
                >
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
                            onclick={() => {
                                senders = receivers.filter(addr => addr !== sender)
                            }}
                        />
                    {/each}
                </div>
            </FormGroup>
            <FormGroup>
                <Label for="receivers">Receiver(s)</Label>
                <Input.Group>
                    <Input.Basic
                        type="email"
                        id="receivers"
                        placeholder="Enter sender@mail.xyz then press 'Space'"
                        onkeyup={addReceiver}
                        onblur={addReceiver}
                    />
                    <Button.Basic
                        type="button"
                        onclick={addReceiver}
                    >
                        <Icon name="add" />
                    </Button.Basic>
                </Input.Group>
                <div class="tags">
                    {#each receivers as receiver}
                        <Badge
                            content={receiver}
                            onclick={() => {
                                receivers = receivers.filter(addr => addr !== receiver)
                            }}
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
                    <Input.Group>
                        <Input.Basic
                            type="email"
                            id="cc"
                            placeholder="Enter sender@mail.xyz then press 'Space'"
                            onkeyup={addCc}
                            onblur={addCc}
                        />
                        <Button.Basic
                            type="button"
                            onclick={addCc}
                        >
                            <Icon name="add" />
                        </Button.Basic>
                    </Input.Group>
                </Collapse>
                <div class="tags">
                    {#each cc as ccAddr}
                        <Badge
                            content={ccAddr}
                            onclick={() => {
                                cc = cc.filter(addr => addr !== ccAddr)
                            }}
                        />
                    {/each}
                </div>
            </FormGroup>
            <FormGroup>
                <Collapse title="Bcc">
                    <Label for="bcc">Bcc</Label>
                    <Input.Group>
                        <Input.Basic
                            type="email"
                            id="bcc"
                            placeholder="Enter sender@mail.xyz then press 'Space'"
                            onkeyup={addBcc}
                            onblur={addBcc}
                        />
                        <Button.Basic
                            type="button"
                            onclick={addBcc}
                        >
                            <Icon name="add" />
                        </Button.Basic>
                    </Input.Group>
                </Collapse>
                <div class="tags">
                    {#each bcc as bccAddr}
                        <Badge
                            content={bccAddr}
                            onclick={() => {
                                bcc = bcc.filter(addr => addr !== bccAddr)
                            }}
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
    }
</style>
