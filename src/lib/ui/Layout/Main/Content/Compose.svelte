<script lang="ts" module>
    export interface ComposeContext {
        flagDraftAsChanged: () => void;
    }
</script>

<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { local } from "$lib/locales";
    import { isStandardFolder } from "$lib/utils";
    import {
        AUTOSAVE_DRAFT_INTERVAL_MS,
        DEFAULT_LANGUAGE,
        SEND_RECALL_DELAY_MS,
    } from "$lib/constants";
    import {
        Folder,
        type Account,
        type OriginalMessageContext,
    } from "$lib/types";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onMount, setContext } from "svelte";
    import { WYSIWYGEditor } from "@bberkay/wysiwygeditor";
    import Form from "$lib/ui/Components/Form";
    import Mailbox, {
        getCurrentMailbox,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import Sender from "./Compose/Sender.svelte";
    import Receivers from "./Compose/Receivers.svelte";
    import Cc from "./Compose/Cc.svelte";
    import Bcc from "./Compose/Bcc.svelte";
    import Subject from "./Compose/Subject.svelte";
    import Body from "./Compose/Body.svelte";
    import Attachments from "./Compose/Attachments.svelte";
    import Action from "./Compose/Action.svelte";
    import Icon from "$lib/ui/Components/Icon";
    import { backToDefault } from "$lib/ui/Layout/Main/Content.svelte";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        originalMessageContext?: OriginalMessageContext;
    }

    let { originalMessageContext }: Props = $props();

    let composeForm: HTMLFormElement | undefined = $state();
    let senderAccount: Account = $state(
        SharedStore.currentAccount !== "home"
            ? SharedStore.currentAccount
            : SharedStore.accounts[0],
    );
    let receiverList: string[] = $state([]);
    let ccList: string[] = $state([]);
    let bccList: string[] = $state([]);
    let subject = $state("");
    let body: WYSIWYGEditor | undefined = $state();

    let isSendingEmail: boolean = $state(false);
    let isSavingDraft: boolean = $state(false);
    let draftAppenduid: string = "";
    let lastDraftSavedTime: string = $state("");
    let isDraftChangedAfterLastSave = false;

    onMount(() => {
        // TODO: Open this later...
        //startAutosaveDraftLoop();
    });

    const flagDraftAsChanged = () => {
        isDraftChangedAfterLastSave = true;
    };
    setContext("compose", { flagDraftAsChanged });

    function startAutosaveDraftLoop() {
        const loop = async () => {
            await saveDraft();
            setTimeout(loop, AUTOSAVE_DRAFT_INTERVAL_MS);
        };
        loop();
    }

    function createDraft(): FormData {
        const formData = new FormData(composeForm);
        formData.set("sender", senderAccount.email_address);
        formData.set("receivers", receiverList.join(","));
        formData.set("cc", ccList.join(","));
        formData.set("bcc", bccList.join(","));
        formData.set("body", body!.getHTMLContent());
        return formData;
    }

    async function deleteDraft() {
        await MailboxController.deleteDraft(
            senderAccount,
            draftAppenduid,
        );
    }

    async function showSentMailbox() {
        if (senderAccount !== SharedStore.currentAccount) {
            SharedStore.currentAccount = senderAccount;
        }

        // Show sent folder of sender which must be the currentAccount
        // at this point.
        if (!isStandardFolder(getCurrentMailbox().folder, Folder.Sent)) {
            const response = await MailboxController.getMailbox(
                SharedStore.currentAccount,
                Folder.Sent,
            );

            if (!response.success) {
                showMessage({
                    title: local.error_sent_mailbox_after_sending_emails[
                        DEFAULT_LANGUAGE
                    ],
                });
                console.error(response.message);
                return;
            }
        }

        showContent(Mailbox);
    }

    async function sendEmail() {
        if (isSendingEmail || isSavingDraft) return;

        const sendTimeout = setTimeout(async () => {
            isSendingEmail = true;

            // Remove draft from drafts folder if exists,
            // before sending them email and create a new/updated
            // one from form.
            await deleteDraft();
            const draft = createDraft();

            let response;
            if (originalMessageContext?.composeType === "reply") {
                response = await MailboxController.replyEmail(
                    originalMessageContext.messageId,
                    draft,
                );
            } else if (originalMessageContext?.composeType === "forward") {
                response = await MailboxController.forwardEmail(
                    originalMessageContext.messageId,
                    draft,
                );
            } else {
                response = await MailboxController.sendEmail(draft);
            }

            isSendingEmail = false;
            if (!response.success) {
                showMessage({
                    title: local.error_send_email_s[DEFAULT_LANGUAGE],
                });
                console.error(response.message);
                return;
            }

            showSentMailbox();
            showToast({ content: "Email sent" });
        }, SEND_RECALL_DELAY_MS);

        showToast({
            content: "Email sending...",
            autoCloseDelay: SEND_RECALL_DELAY_MS,
            onUndo: () => {
                clearTimeout(sendTimeout);
            },
        });
    }

    const saveDraft = async () => {
        if (isSendingEmail || isSavingDraft || !isDraftChangedAfterLastSave)
            return;

        isSavingDraft = true;

        const draft = createDraft();
        const response = await MailboxController.saveDraft(
            draft,
            draftAppenduid,
        );

        if (response.success && response.data) {
            draftAppenduid = response.data;
        } else {
            showMessage({
                title: local.error_save_email_s_as_draft[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
        }

        isSavingDraft = false;
        isDraftChangedAfterLastSave = false;
        lastDraftSavedTime = new Date(Date.now()).toLocaleString();
    };

    const handleSendEmailForm = async () => {
        if (!senderAccount || receiverList.length === 0) {
            showMessage({
                title: "Provide at least one sender and one receiver.",
            });
            console.error("Provide at least one sender and one receiver.");
            return;
        }

        if (!subject) {
            showConfirm({
                title: local.are_you_certain_subject_is_empty[DEFAULT_LANGUAGE],
                onConfirmText: local.yes_send[DEFAULT_LANGUAGE],
                onConfirm: sendEmail,
            });
            return;
        }

        if (!body!.getHTMLContent()) {
            showConfirm({
                title: local.are_you_certain_body_is_empty[DEFAULT_LANGUAGE],
                onConfirmText: local.yes_send[DEFAULT_LANGUAGE],
                onConfirm: sendEmail,
            });
            return;
        }

        await sendEmail();
    };
</script>

<div class="compose">
    <Button.Basic
        type="button"
        class="btn-inline"
        onclick={backToDefault}
    >
        <Icon name="back" />
    </Button.Basic>

    <h2 class="compose-title">Compose</h2>
    <Form
        class="compose-form"
        bind:element={composeForm}
        onsubmit={handleSendEmailForm}
    >
        <Sender bind:senderAccount />
        <Receivers bind:receiverList {originalMessageContext} />
        <Cc bind:ccList />
        <Bcc bind:bccList />
        <Subject bind:value={subject} {originalMessageContext} />
        <Body bind:editor={body} {originalMessageContext} />
        <Attachments />
        <Action bind:isSendingEmail bind:isSavingDraft {saveDraft} {deleteDraft} />
    </Form>
    {#if lastDraftSavedTime}
        <span class="draft-saved-feedback">
            Draft saved at {lastDraftSavedTime}
        </span>
    {/if}
</div>

<style>
    :global {
        .compose {
            display: flex;
            flex-direction: column;
            padding: var(--spacing-xl) var(--spacing-2xl);
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-sm);
            width: 75%;
            height: 100%;

            & .compose-form {
                overflow-x: hidden;
                overflow-y: auto;
                height: 100%;
                margin-bottom: 50px;
                padding-right: 30px; /* because of the scrollbar */
            }

            & .compose-title {
                margin-bottom: var(--spacing-lg);
            }
        }
    }
</style>
