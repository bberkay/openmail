<script lang="ts">
    import {
        type Email as TEmail,
    } from "$lib/types";
    import { getCurrentMailbox, type EmailSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import Selection from "./Content/Selection.svelte";
    import GroupDate from "./Content/GroupDate.svelte";
    import EmailPreview from "./Content/EmailPreview.svelte";

    interface Props {
        emailSelection: EmailSelection;
    }

    type DateGroup =
        | (typeof local.today)[typeof DEFAULT_LANGUAGE]
        | (typeof local.yesterday)[typeof DEFAULT_LANGUAGE]
        | (typeof local.this_week)[typeof DEFAULT_LANGUAGE]
        | (typeof local.this_month)[typeof DEFAULT_LANGUAGE]
        | (typeof local.older)[typeof DEFAULT_LANGUAGE];

    let { emailSelection = $bindable() }: Props = $props();

    let groupedEmailsByDate: Record<DateGroup, TEmail[]> = $derived.by(() => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const lastWeekStart = new Date(today);
        lastWeekStart.setDate(lastWeekStart.getDate() - 7);

        const lastMonthStart = new Date(today);
        lastMonthStart.setMonth(lastMonthStart.getMonth() - 1);

        const groupedEmails: Record<DateGroup, TEmail[]> = {
            [local.today[DEFAULT_LANGUAGE]]: [],
            [local.yesterday[DEFAULT_LANGUAGE]]: [],
            [local.this_week[DEFAULT_LANGUAGE]]: [],
            [local.this_month[DEFAULT_LANGUAGE]]: [],
            [local.older[DEFAULT_LANGUAGE]]: [],
        };

        getCurrentMailbox().emails.current.forEach((email: TEmail) => {
            const emailDate = new Date(email.date);
            emailDate.setHours(0, 0, 0, 0);

            if (emailDate.getTime() === today.getTime()) {
                groupedEmails[local.today[DEFAULT_LANGUAGE]].push(email);
            } else if (emailDate.getTime() === yesterday.getTime()) {
                groupedEmails[local.yesterday[DEFAULT_LANGUAGE]].push(email);
            } else if (emailDate >= lastWeekStart && emailDate < yesterday) {
                groupedEmails[local.this_week[DEFAULT_LANGUAGE]].push(email);
            } else if (
                emailDate >= lastMonthStart &&
                emailDate < lastWeekStart
            ) {
                groupedEmails[local.this_month[DEFAULT_LANGUAGE]].push(email);
            } else {
                groupedEmails[local.older[DEFAULT_LANGUAGE]].push(email);
            }
            });

        return groupedEmails;
    });
</script>

<div class="mailbox">
    <Selection bind:emailSelection />
    {#each Object.entries(groupedEmailsByDate) as [groupDate, groupedEmails]}
        {#if groupedEmails.length > 0}
            <GroupDate {groupDate} />
            <div class="email-preview-group">
                {#each groupedEmails as email}
                    <EmailPreview bind:emailSelection {email} />
                {/each}
            </div>
        {/if}
    {/each}
</div>

<style>
    :global {
        .mailbox {
            display: flex;
            flex-direction: column;
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-sm);
            width: 80%;
            padding: 0;
            height: 100%;
            overflow-x: hidden;
            overflow-y: scroll;
        }
    }
</style>
