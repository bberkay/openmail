<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Mailbox, Folder } from "$lib/types";
    import Toolbox from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox.svelte";
    import Content from "$lib/ui/Layout/Main/Content/Mailbox/Content.svelte";

    let emailSelection: "1:*" | string[] = $state([]);
    let currentMailbox = $derived.by(() => {
        if (SharedStore.currentAccount === "home") {
            let currentMailbox: Mailbox = {
                total: 0,
                emails: { prev: [], current: [], next: [] },
                folder: Folder.Inbox // mailboxes are going to be INBOX while selecting account to "home"
            };
            Object.values(SharedStore.mailboxes).forEach((mailbox) => {
                currentMailbox.total += mailbox.total;
                currentMailbox.emails.prev.push(...mailbox.emails.prev);
                currentMailbox.emails.current.push(...mailbox.emails.current);
                currentMailbox.emails.next.push(...mailbox.emails.next);
            });
            Object.values(currentMailbox.emails).forEach((emails) => {
                emails.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
            })
            return currentMailbox;
        } else {
            return SharedStore.mailboxes[
                SharedStore.currentAccount.email_address
            ]
        }
    });
</script>

<Toolbox bind:emailSelection {currentMailbox} />
<Content bind:emailSelection {currentMailbox} />
