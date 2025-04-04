<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email } from "$lib/types";
    import { EMAIL_PAGINATION_TEMPLATE } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        account: Account;
        email: Email;
    }

    let { account, email }: Props = $props();

    const currentMailbox = SharedStore.mailboxes[account.email_address];

    let currentOffset = $state(
        currentMailbox.emails.current.findIndex((em) => em.uid === email.uid),
    );

    const updateShownEmail = async (): Promise<void> => {
        const uid = currentMailbox.emails.current[currentOffset].uid;

        const response = await MailboxController.getEmailContent(
            account,
            currentMailbox.folder,
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
        if (currentOffset < 1) {
            // TODO: prev calculation.
            return;
        }

        currentOffset -= 1;
        updateShownEmail();
    };

    const getNextEmail = async () => {
        if (currentOffset >= currentMailbox.total) {
            // TODO: what if currentoffset is bigger than emails.current.length, next calculation.
            return;
        }

        currentOffset += 1;
        updateShownEmail();
    };
</script>

<div class="toolbox-right">
    <div class="pagination">
        <Button.Action
            type="button"
            class="btn-inline {currentOffset < 1 ? 'disabled' : ''}"
            onclick={getPreviousEmail}
        >
            Prev
        </Button.Action>
        <small>
            {EMAIL_PAGINATION_TEMPLATE.replace(
                "{current}",
                (currentOffset + 1).toString(),
            )
                .replace("{total}", currentMailbox.total.toString())
                .trim()}
        </small>
        <Button.Action
            type="button"
            class="btn-inline {currentOffset >= currentMailbox.total
                ? 'disabled'
                : ''}"
            onclick={getNextEmail}
        >
            Next
        </Button.Action>
    </div>
</div>
