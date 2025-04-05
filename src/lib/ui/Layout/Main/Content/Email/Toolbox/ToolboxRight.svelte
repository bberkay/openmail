<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MAILBOX_LENGTH, MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email, Folder } from "$lib/types";
    import { EMAIL_PAGINATION_TEMPLATE } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";
    import { getCurrentMailbox, paginateMailboxBackward, paginateMailboxForward } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        account: Account;
        email: Email;
    }

    let { account, email }: Props = $props();

    let currentOffset = $state(
        getCurrentMailbox().emails.current.findIndex((em) => em.uid === email.uid) + 1
    );

    const updateShownEmail = async (): Promise<void> => {
        const uid = getCurrentMailbox().emails.current[currentOffset].uid;

        const response = await MailboxController.getEmailContent(
            account,
            getCurrentMailbox().folder,
            uid,
        );

        if (!response.success || !response.data) {
            showMessage({ content: "Error while getting email content." });
            console.error(response.message);
            return;
        }

        email = response.data;
    };

    const getPreviousEmail = async () => {
        if (currentOffset <= 1) return;
        if (currentOffset - 1 % MAILBOX_LENGTH == 0) {
            await paginateMailboxBackward(currentOffset - 1);
        }

        currentOffset -= 1;
        updateShownEmail();
    };

    const getNextEmail = async () => {
        if (currentOffset >= getCurrentMailbox().total) return;
        if (currentOffset + 1 % MAILBOX_LENGTH == 1) {
            await paginateMailboxBackward(currentOffset + 1);
        }

        currentOffset += 1;
        updateShownEmail();
    };
</script>

<div class="toolbox-right">
    {#if currentOffset > 0}
        <div class="pagination">
            <Button.Action
                type="button"
                class="btn-inline {currentOffset == 1 ? 'disabled' : ''}"
                onclick={getPreviousEmail}
            >
                Prev
            </Button.Action>
            <small>
                {EMAIL_PAGINATION_TEMPLATE.replace(
                    "{current}",
                    (currentOffset + 1).toString(),
                )
                .replace("{total}", getCurrentMailbox().total.toString())
                .trim()}
            </small>
            <Button.Action
                type="button"
                class="btn-inline { currentOffset >= getCurrentMailbox().total
                ? 'disabled'
                : ''}"
                onclick={getNextEmail}
            >
                Next
            </Button.Action>
        </div>
    {/if}
</div>
