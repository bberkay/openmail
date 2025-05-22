<script lang="ts">
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email } from "$lib/types";
    import { getEmailPaginationTemplate } from "$lib/templates";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import {
        getCurrentMailbox,
        paginateMailboxBackward,
        paginateMailboxForward,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { SharedStore } from "$lib/stores/shared.svelte";

    interface Props {
        account: Account;
        email: Email;
        currentOffset: number;
    }

    let {
        account,
        email = $bindable(),
        currentOffset = $bindable(),
    }: Props = $props();

    const updateShownEmail = async (): Promise<void> => {
        const uid = getCurrentMailbox().emails.current[currentOffset].uid;

        const response = await MailboxController.getEmailContent(
            account,
            getCurrentMailbox().folder,
            uid,
        );

        if (!response.success || !response.data) {
            showMessage({ title: local.error_get_email_content[DEFAULT_LANGUAGE] });
            console.error(response.message);
            return;
        }

        email = response.data;
    };

    const getPreviousEmail = async () => {
        if (currentOffset <= 1)
            return;

        const MAILBOX_LENGTH = SharedStore.preferences.mailboxLength;
        if (currentOffset - (1 % MAILBOX_LENGTH) == 0) {
            await paginateMailboxBackward(currentOffset - 1);
        }

        currentOffset -= 1;
        updateShownEmail();
    };

    const getNextEmail = async () => {
        if (currentOffset >= getCurrentMailbox().total)
            return;

        const MAILBOX_LENGTH = SharedStore.preferences.mailboxLength;
        if (currentOffset + (1 % MAILBOX_LENGTH) == 1) {
            await paginateMailboxForward(currentOffset + 1);
        }

        currentOffset += 1;
        updateShownEmail();
    };
</script>

{#if currentOffset > 0}
    <div class="pagination">
        <Button.Action
            type="button"
            class="btn-inline {currentOffset == 1 ? 'disabled' : ''}"
            onclick={getPreviousEmail}
        >
            <Icon name="prev" />
        </Button.Action>
        <small>
            {getEmailPaginationTemplate(
                (currentOffset + 1).toString(),
                getCurrentMailbox().total.toString(),
            )}
        </small>
        <Button.Action
            type="button"
            class="btn-inline {currentOffset >= getCurrentMailbox().total
                ? 'disabled'
                : ''}"
            onclick={getNextEmail}
        >
            <Icon name="next" />
        </Button.Action>
    </div>
{/if}
