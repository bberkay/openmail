<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email } from "$lib/types";
    import { EMAIL_PAGINATION_TEMPLATE } from '$lib/constants';
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        account: Account;
        email: Email;
    }

    let {
        account,
        email
    }: Props = $props();

    let currentMailbox = $derived(SharedStore.mailboxes.find(
        task => task.result.folder === SharedStore.currentFolder
    )!.result);

    let totalEmailCount = $derived(currentMailbox.total);
    let currentOffset = $derived(currentMailbox.emails.findIndex(
        em => em.uid === email.uid
    ) + 1);

    const setEmailByUid = async (uid: string): Promise<void> => {
        const response = await MailboxController.getEmailContent(
            account,
            currentMailbox.folder,
            uid
        );

        if (!response.success || !response.data) {
            showMessage({content: "Error while getting email content."});
            console.error(response.message);
            return;
        }

        email = response.data;
    }

    const getPreviousEmail = async () => {
        const previousUidIndex = currentMailbox.emails.findIndex(
            em => em.uid === email.uid
        ) - 1;
        if (previousUidIndex < 0)
            return;

        setEmailByUid(currentMailbox.emails[previousUidIndex].uid);
    }

    const getNextEmail = async () => {
        const nextUidIndex = currentMailbox.emails.findIndex(
            em => em.uid === email.uid
        ) - 1;
        if (nextUidIndex < 0)
            return;

        setEmailByUid(currentMailbox.emails[nextUidIndex].uid);
    }
</script>

<div class="toolbox-right">
    <div class="pagination">
        <Button.Action
            type="button"
            class="btn-inline {currentOffset < 2 ? "disabled" : ""}"
            onclick={getPreviousEmail}
        >
            Prev
        </Button.Action>
        <small>
            {
                EMAIL_PAGINATION_TEMPLATE
                    .replace("{current}", Math.max(1, currentOffset).toString())
                    .replace("{total}", totalEmailCount.toString())
                    .trim()
            }
        </small>
        <Button.Action
            type="button"
            class="btn-inline {currentOffset >= totalEmailCount ? "disabled" : ""}"
            onclick={getNextEmail}
        >
            Next
        </Button.Action>
    </div>
</div>
