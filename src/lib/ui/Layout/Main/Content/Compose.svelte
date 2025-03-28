<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { extractEmailAddress, isStandardFolder } from "$lib/utils";
    import { REPLY_TEMPLATE, FORWARD_TEMPLATE } from "$lib/constants";
    import { Folder } from "$lib/types";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onMount } from "svelte";
    import { WYSIWYGEditor } from "@bberkay/wysiwygeditor";
    import {
        createSenderAddress,
        escapeHTML,
        addEmailToAddressList,
    } from "$lib/utils";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import Icon from "$lib/ui/Components/Icon";
    import Collapse from "$lib/ui/Components/Collapse";
    import Form, { FormGroup } from "$lib/ui/Components/Form";
    import Badge from "$lib/ui/Components/Badge";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        originalMessageContext?: {
            composeType: "reply" | "forward";
            originalMessageId: string;
            originalSender: string;
            originalReceivers: string;
            originalSubject: string;
            originalBody: string;
            originalDate: string;
        };
    }

    let { originalMessageContext }: Props = $props();

    let composeWrapper: HTMLElement;
    let receiverInput: HTMLInputElement;
    let ccInput: HTMLInputElement;
    let bccInput: HTMLInputElement;

    let body: WYSIWYGEditor;
    let senders: string[] = $state([]);
    let receivers: string[] = $state(
        originalMessageContext
            ? originalMessageContext.originalReceivers
                  .split(",")
                  .map((receiver) => extractEmailAddress(receiver))
            : [],
    );
    let cc: string[] = $state([]);
    let bcc: string[] = $state([]);

    onMount(() => {
        receiverInput = composeWrapper.querySelector('input[id="receivers"]')!;
        ccInput = composeWrapper.querySelector('input[id="cc"]')!;
        bccInput = composeWrapper.querySelector('input[id="bcc"]')!;

        body = new WYSIWYGEditor("body");
        body.init();
        if (originalMessageContext) {
            body.addFullHTMLPage(
                (originalMessageContext.composeType == "reply"
                    ? REPLY_TEMPLATE
                    : FORWARD_TEMPLATE
                )
                    .replace(
                        "{original_sender}",
                        escapeHTML(originalMessageContext.originalSender || ""),
                    )
                    .replace(
                        "{original_receivers}",
                        escapeHTML(
                            originalMessageContext.originalReceivers || "",
                        ),
                    )
                    .replace(
                        "{original_subject}",
                        originalMessageContext.originalSubject || "",
                    )
                    .replace(
                        "{original_body}",
                        originalMessageContext.originalBody || "",
                    )
                    .replace(
                        "{original_date}",
                        originalMessageContext.originalDate || "",
                    ),
            );
        }
    });

    const addReceiver = (e: Event) => {
        addEmailToAddressList(e, receiverInput, receivers);
    };

    const addCc = (e: Event) => {
        addEmailToAddressList(e, ccInput, cc);
    };

    const addBcc = (e: Event) => {
        addEmailToAddressList(e, bccInput, bcc);
    };

    const sendEmail = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);

        formData.set("sender", senders.join(","));
        formData.set("receivers", receivers.join(","));

        if (!formData.get("sender")) {
            showMessage({ content: "At least one sender must be added" });
            console.error("At least one sender must be added");
            return;
        }
        if (!formData.get("receivers")) {
            showMessage({ content: "At least one receiver must be added" });
            console.error("At least one receiver must be added");
            return;
        }

        formData.set("cc", cc.join(","));
        formData.set("bcc", bcc.join(","));
        formData.set("body", body.getHTMLContent());

        let response;
        if (originalMessageContext) {
            if (originalMessageContext.composeType === "reply") {
                response = await MailboxController.replyEmail(
                    formData,
                    originalMessageContext.originalMessageId,
                );
            } else {
                response = await MailboxController.forwardEmail(
                    formData,
                    originalMessageContext.originalMessageId,
                );
            }
        } else {
            response = await MailboxController.sendEmail(formData);
        }

        if (!response.success) {
            showMessage({ content: "Error, email could not sent." });
            console.error(response!.message);
            return;
        }

        body.clear();

        // Show first sender's Folder.Sent mailbox.
        SharedStore.currentFolder = SharedStore.standardFolders[
            senders[0]
        ].find((folder: string) =>
            isStandardFolder(folder, Folder.Sent)
        )!;
        // TODO: Fetch sent folder
        showContent(Mailbox);
    };
</script>

<div class="compose" bind:this={composeWrapper}>
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
                        {@const sender = createSenderAddress(
                            account.email_address,
                            account.fullname,
                        )}
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
                                senders = receivers.filter(
                                    (addr) => addr !== sender,
                                );
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
                    <Button.Basic type="button" onclick={addReceiver}>
                        <Icon name="add" />
                    </Button.Basic>
                </Input.Group>
                <div class="tags">
                    {#each receivers as receiver}
                        <Badge
                            content={receiver}
                            onclick={() => {
                                receivers = receivers.filter(
                                    (addr) => addr !== receiver,
                                );
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
                    value={originalMessageContext
                        ? (originalMessageContext.composeType == "reply"
                              ? "Re: "
                              : "Fwd: ") +
                          originalMessageContext.originalSubject
                        : ""}
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
                        <Button.Basic type="button" onclick={addCc}>
                            <Icon name="add" />
                        </Button.Basic>
                    </Input.Group>
                </Collapse>
                <div class="tags">
                    {#each cc as ccAddr}
                        <Badge
                            content={ccAddr}
                            onclick={() => {
                                cc = cc.filter((addr) => addr !== ccAddr);
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
                        <Button.Basic type="button" onclick={addBcc}>
                            <Icon name="add" />
                        </Button.Basic>
                    </Input.Group>
                </Collapse>
                <div class="tags">
                    {#each bcc as bccAddr}
                        <Badge
                            content={bccAddr}
                            onclick={() => {
                                bcc = bcc.filter((addr) => addr !== bccAddr);
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
                <Input.File name="attachments" id="attachments" multiple />
            </FormGroup>
            <Button.Basic type="submit" id="send-email" style="margin-top:10px">
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
