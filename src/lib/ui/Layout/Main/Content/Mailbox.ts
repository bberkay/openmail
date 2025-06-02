import { getContext } from "svelte";
import { type MailboxContext, CONTEXT_KEY } from "./Mailbox.svelte";

export function getMailboxContext(): MailboxContext {
    return getContext(CONTEXT_KEY);
}
