<script lang="ts">
    import { onMount, onDestroy, mount, unmount } from "svelte";
    import {
        getSenderToReceiverTemplate,
        getSenderToReceiverAndOthersTemplate,
    } from "$lib/templates";
    import {
    compactEmailDate,
        extractEmailAddress,
        extractFullname,
    } from "$lib/utils";
    import Others from "./Others.svelte";
    import { type Account, type Email } from "$lib/types";

    interface Props {
        account: Account;
        email: Email;
    }

    let {
        account,
        email
    }: Props = $props();

    let senderToReceiver: HTMLElement;
    let mountedOthers: Record<string, any> | null = null;
    onMount(() => {
        const senderToReceiverTemplate =
            email.receivers.split(",").length > 1 || email.cc || email.bcc
                ? getSenderToReceiverAndOthersTemplate
                : getSenderToReceiverTemplate;

        senderToReceiver.innerHTML = senderToReceiverTemplate(
            extractFullname(email.sender),
            extractEmailAddress(email.sender),
            account.fullname || "",
            account.email_address,
            compactEmailDate(email.date, false),
        );

        const others = senderToReceiver.querySelector<HTMLElement>(".others");
        if (others) {
            mountedOthers = mount(Others, {
                target: others,
                props: {
                    toggleText: others.innerText,
                    receivers: email.receivers,
                    cc: email.cc,
                    bcc: email.bcc,
                },
            });
        }
    });

    onDestroy(() => {
        if (mountedOthers) {
            unmount(mountedOthers);
        }
    });
</script>

<div class="sender-to-receiver" bind:this={senderToReceiver}></div>

<style>
    :global {
        .email-content .sender-to-receiver {
            margin-top: var(--spacing-xs);
            color: var(--color-text-secondary);
            font-size: var(--font-size-sm);
        }
    }
</style>
