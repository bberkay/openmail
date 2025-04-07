<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { extractEmailAddress, isStandardFolder } from "$lib/utils";
    import { REPLY_TEMPLATE, FORWARD_TEMPLATE } from "$lib/constants";
    import { Folder, type Account, type Draft } from "$lib/types";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onDestroy, onMount } from "svelte";
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
    import Mailbox, {
        getCurrentMailbox,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import type { PostResponse } from "$lib/services/ApiService";

    const AUTO_SAVE_DRAFT_INTERVAL = 1000 * 5;

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
    let composeForm: HTMLFormElement;
    let receiverInput: HTMLInputElement;
    let ccInput: HTMLInputElement;
    let bccInput: HTMLInputElement;
    let subjectInput: HTMLInputElement;

    let senderAccounts: Account[] = $state([]);
    let isSendingEmail: boolean = $state(false);
    let draftAppenduids: { [account: string]: string } = {};
    let draftLoopTimeout: ReturnType<typeof setTimeout>;
    let isSavingDraft: boolean = $state(false);
    let draftChangedAfterLastSave: boolean = true;

    let body: WYSIWYGEditor;
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
        composeForm = composeWrapper.querySelector('form[id="compose-form"]')!;
        receiverInput = composeForm.querySelector('input[id="receivers"]')!;
        ccInput = composeForm.querySelector('input[id="cc"]')!;
        bccInput = composeForm.querySelector('input[id="bcc"]')!;
        subjectInput = composeForm.querySelector('input[id="subject"]')!;

        body = new WYSIWYGEditor("body");
        body.init();
        body.onChange = () => {
            draftChangedAfterLastSave = true;
        };
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

        startAutoSaveDraftLoop();
    });

    onDestroy(() => {
        body.clear();
        if (draftLoopTimeout) clearTimeout(draftLoopTimeout);
    });

    function startAutoSaveDraftLoop() {
        if (draftLoopTimeout) return;

        const loop = async () => {
            await saveEmailsAsDrafts();
            draftLoopTimeout = setTimeout(loop, AUTO_SAVE_DRAFT_INTERVAL);
        };

        loop();
    }

    function createFormDataOfDraft(sender: string): FormData {
        const formData = new FormData(composeForm);
        formData.set("sender", sender);
        formData.set("receivers", receivers.join(","));
        formData.set("cc", cc.join(","));
        formData.set("bcc", bcc.join(","));
        formData.set("body", body.getHTMLContent());
        return formData;
    }

    async function saveEmailAsDraft(sender: string): Promise<PostResponse> {
        const formData = createFormDataOfDraft(sender);
        const response = await MailboxController.saveEmailAsDraft(
            formData,
            draftAppenduids[sender],
        );

        if (response.success && response.data) {
            draftAppenduids[sender] = response.data;
        }

        return response;
    }

    async function sendEmail(sender: string): Promise<PostResponse> {
        const draft = createFormDataOfDraft(sender);

        // Remove saved draft before sending as email.
        if (Object.hasOwn(draftAppenduids, sender)) {
            // Since we are going to redirect user to Sent folder
            // we don't need to send `offset` argument(which there
            // is no current connection between `Mailbox` and `Compose`
            // components to get `offset` anyway.) to `deleteEmails()`.
            await MailboxController.deleteEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === sender,
                )!,
                draftAppenduids[sender],
                Folder.Drafts,
            );
        }

        let sentResponse;
        if (originalMessageContext) {
            if (originalMessageContext.composeType === "reply") {
                sentResponse = await MailboxController.replyEmail(
                    originalMessageContext.originalMessageId,
                    draft,
                );
            } else {
                sentResponse = await MailboxController.forwardEmail(
                    originalMessageContext.originalMessageId,
                    draft,
                );
            }
        } else {
            sentResponse = await MailboxController.sendEmail(draft);
        }

        return sentResponse;
    }

    const addSenderAccount = (senderEmailAddr: string) => {
        const senderAccount = SharedStore.accounts.find(
            (acc) => acc.email_address === senderEmailAddr,
        )!;
        senderAccounts.push(senderAccount);
    };

    const addReceiver = (e: Event) => {
        addEmailToAddressList(e, receiverInput, receivers);
        draftChangedAfterLastSave = true;
    };

    const addCc = (e: Event) => {
        addEmailToAddressList(e, ccInput, cc);
        draftChangedAfterLastSave = true;
    };

    const addBcc = (e: Event) => {
        addEmailToAddressList(e, bccInput, bcc);
        draftChangedAfterLastSave = true;
    };

    const saveEmailsAsDrafts = async () => {
        if (isSendingEmail || isSavingDraft || !draftChangedAfterLastSave)
            return;
        isSavingDraft = true;

        const results = await Promise.allSettled(
            senderAccounts.map(async (account) => {
                const response = await saveEmailAsDraft(
                    createSenderAddress(
                        account.email_address,
                        account.fullname,
                    ),
                );
                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");

        if (failed.length > 0) {
            showMessage({ content: "Error, email could not saved as draft." });
            failed.forEach((f) => console.error(f.reason));
        }

        isSavingDraft = false;
        draftChangedAfterLastSave = false;
    };

    const sendEmails = async () => {
        const confirmWrapper = async () => {
            isSendingEmail = true;
            const results = await Promise.allSettled(
                senderAccounts.map(async (account) => {
                    const response = await sendEmail(
                        createSenderAddress(
                            account.email_address,
                            account.fullname,
                        ),
                    );
                    if (!response.success) {
                        throw new Error(response.message);
                    }
                }),
            );

            const failed = results.filter((r) => r.status === "rejected");

            if (failed.length > 0) {
                showMessage({
                    content: "Error while sending emails.",
                });
                failed.forEach((f) => console.error(f.reason));
                isSendingEmail = false;
                return;
            }

            if (
                SharedStore.currentAccount === "home" ||
                !senderAccounts.includes(SharedStore.currentAccount)
            ) {
                SharedStore.currentAccount = senderAccounts[0];
            }

            // Show first sender's Folder.Sent mailbox.
            if (!isStandardFolder(getCurrentMailbox().folder, Folder.Sent)) {
                const response = await MailboxController.getMailbox(
                    SharedStore.currentAccount,
                    Folder.Sent,
                );

                if (!response.success) {
                    showMessage({
                        content:
                            "Failed to retrieve sent folder. Please try again",
                    });
                    console.error(response.message);
                    return;
                }
            }

            isSendingEmail = false;
            showContent(Mailbox);
        };

        if (isSendingEmail || isSavingDraft) return;

        if (receivers.length == 0) {
            showMessage({ content: "At least one receiver must be added" });
            console.error("At least one receiver must be added");
            return;
        }

        if (!subjectInput.value) {
            showConfirm({
                content:
                    "The subject field is empty. Are you sure you want to send the email without a subject?",
                onConfirmText: "Yes, send.",
                onConfirm: confirmWrapper,
            });
            return;
        }

        if (!body.getHTMLContent()) {
            showConfirm({
                content:
                    "The message body is empty. Are you sure you want to send the email without any content?",
                onConfirmText: "Yes, send.",
                onConfirm: confirmWrapper,
            });
        }
    };
</script>

<div class="compose" bind:this={composeWrapper}>
    <Form onsubmit={sendEmails} id="compose-form">
        <div>
            <FormGroup>
                <Label for="senders">Sender(s)</Label>
                <Select.Root
                    id="senders"
                    placeholder="Add sender"
                    onchange={addSenderAccount}
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
                    {#each senderAccounts as account}
                        <Badge
                            content={account.email_address}
                            onclick={() => {
                                senderAccounts = senderAccounts.filter(
                                    (addr) =>
                                        addr.email_address !==
                                        account.email_address,
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
                    onkeyup={() => {
                        draftChangedAfterLastSave = true;
                    }}
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
            <div style="margin-top:10px">
                <Button.Basic
                    type="submit"
                    id="send-email"
                    class="btn-cta"
                    disabled={isSendingEmail || isSavingDraft}
                >
                    Send Email
                </Button.Basic>
                <Button.Action
                    type="button"
                    id="save-emails-as-drafts"
                    class="btn-outline"
                    onclick={saveEmailsAsDrafts}
                    disabled={isSendingEmail || isSavingDraft}
                >
                    Save as Draft
                </Button.Action>
            </div>
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
