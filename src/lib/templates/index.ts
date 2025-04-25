import { local } from "$lib/locales";
import { DEFAULT_LANGUAGE } from "$lib/constants";

/**
 * ----------------------------------------------------------------------------
 * Generally used constants
 * ----------------------------------------------------------------------------
 */
export function getNotImplementedTemplate(feature: string) {
    return local.feature_not_implemented[DEFAULT_LANGUAGE].replace(
        "{feature}",
        feature,
    );
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Components/Select/Select.svelte
 * ----------------------------------------------------------------------------
 */
export function getNoMatchFoundTemplate() {
    return `
    <div class="no-results">${local.no_match_found[DEFAULT_LANGUAGE]}</div>
    `;
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Landing/Register/AccountList.svelte
 * ----------------------------------------------------------------------------
 */
export function getFailedAccountsTemplate(failed_account_list_items: string) {
    return `
    <p>${local.failed_accounts_are[DEFAULT_LANGUAGE]}</p>
    <ul>
        {failed_account_list_items}
    </ul>
    `.replace("{failed_account_list_items}", failed_account_list_items);
}

export function getSelectedAccountTemplate(count: string) {
    return local.account_selected[DEFAULT_LANGUAGE].replace("{count}", count);
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Navbar/Search.svelte
 * ----------------------------------------------------------------------------
 */
export function getSearchForAccountTemplate(account: string) {
    return local.search_for_account[DEFAULT_LANGUAGE].replace(
        "{account}",
        account.toString(),
    );
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Navbar/Notifications.svelte
 * ----------------------------------------------------------------------------
 */
export function getNewMessageTemplate(
    sender_fullname: string,
    sender_email: string,
    receiver_email: string,
    sent_at: string,
) {
    return local.sender_to_receiver_of_new_message[DEFAULT_LANGUAGE].replace(
        "{sender_fullname}",
        sender_fullname,
    )
        .replace("{sender_email}", sender_email)
        .replace("{receiver_email}", receiver_email)
        .replace("{sent_at}", sent_at);
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Navbar/Account.svelte
 * ----------------------------------------------------------------------------
 */
export function getLogoutFromTemplate(account: string) {
    return local.logout_from_account[DEFAULT_LANGUAGE].replace(
        "{account}",
        account.toString(),
    );
}

export function getNotLoggedOutFromTemplate(account: string) {
    return local.error_not_logged_out_account[DEFAULT_LANGUAGE].replace(
        "{account}",
        account.toString(),
    );
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content.svelte
 * ----------------------------------------------------------------------------
 */
export function getFailedMailboxOrFoldersTemplate(
    failed_mailbox_list_items: string,
    failed_folder_list_items: string,
) {
    return `
     <p>${local.accounts_of_failed_mailboxes_are[DEFAULT_LANGUAGE]}</p>
     <ul>
        {failed_mailbox_list_items}
     </ul>
     <p>${local.accounts_of_failed_folders_are[DEFAULT_LANGUAGE]}</p>
     <ul>
        {failed_folder_list_items}
     </ul>
     `
        .replace("{failed_mailbox_list_items}", failed_mailbox_list_items)
        .replace("{failed_folder_list_items}", failed_folder_list_items);
}

export function getFailedItemTemplate(email_address: string) {
    return `<li>{email_address}</li>`.replace("{email_address}", email_address);
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content/Compose.svelte
 * ----------------------------------------------------------------------------
 */
export function getReplyTemplate(
    original_date: string,
    original_sender: string,
    original_body: string,
) {
    return `
    <br/><br/>
    <div>
        ${local.on_wrote[DEFAULT_LANGUAGE]}<br/>
        <blockquote style="margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex">
            {original_body}
        </blockquote>
    </div>
    `
        .replace("{original_date}", original_date)
        .replace("{original_sender}", original_sender)
        .replace("{original_body}", original_body);
}

export function getForwardTemplate(
    original_sender: string,
    original_date: string,
    original_subject: string,
    original_receivers: string,
    original_body: string,
) {
    return `
    <div>
        ${local.forwarded_message[DEFAULT_LANGUAGE]}:<br/>
        ${local.from[DEFAULT_LANGUAGE]}: {original_sender}<br/>
        ${local.date[DEFAULT_LANGUAGE]}: {original_date}<br/>
        ${local.subject[DEFAULT_LANGUAGE]}: {original_subject}<br/>
        ${local.to[DEFAULT_LANGUAGE]}: {original_receivers}<br/>
        <blockquote style=\"margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex\">
            {original_body}
        </blockquote>
    </div>
    `
        .replace("{original_sender}", original_sender)
        .replace("{original_date}", original_date)
        .replace("{original_subject}", original_subject)
        .replace("{original_receivers}", original_receivers)
        .replace("{original_body}", original_body);
}

export function getSenderToReceiverTemplate(
    sender_fullname: string,
    sender_email: string,
    receiver_email: string,
    sent_at: string,
) {
    return local.sender_to_receiver[DEFAULT_LANGUAGE].replace(
        "{sender_fullname}",
        sender_fullname,
    )
        .replace("{sender_email}", sender_email)
        .replace("{receiver_email}", receiver_email)
        .replace("{sent_at}", sent_at);
}

export function getSenderToReceiverAndOthersTemplate(
    sender_fullname: string,
    sender_email: string,
    receiver_email: string,
    sent_at: string,
) {
    return local.sender_to_receiver_and_others[DEFAULT_LANGUAGE].replace(
        "{sender_fullname}",
        sender_fullname,
    )
        .replace("{sender_email}", sender_email)
        .replace("{receiver_email}", receiver_email)
        .replace("{sent_at}", sent_at);
}

export function getAttachmentTemplate(
    attachment_name: string,
    attachment_size: string,
) {
    return `
    {attachment_name} ({attachment_size})
    `
        .replace("{attachment_name}", attachment_name)
        .replace("{attachment_size}", attachment_size);
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content/Email.svelte
 * ----------------------------------------------------------------------------
 */
export function getEmailPaginationTemplate(
    current: string | number,
    total: string | number,
) {
    return local.current_email_offset[DEFAULT_LANGUAGE].replace(
        "{current}",
        String(current),
    ).replace("{total}", String(total));
}

export function getErrorMarkEmailsTemplate(mark: string) {
    return local.error_mark_email_s[DEFAULT_LANGUAGE].replace("{mark}", mark);
}

export function getErrorUnmarkEmailsTemplate(mark: string) {
    return local.error_unmark_email_s[DEFAULT_LANGUAGE].replace("{mark}", mark);
}

export function getErrorCopyEmailsTemplate(
    source_folder: string,
    destination_folder: string,
) {
    return local.error_copy_email_s[DEFAULT_LANGUAGE].replace(
        "{source_folder}",
        source_folder,
    ).replace("{destination_folder}", destination_folder);
}

export function getErrorMoveEmailsTemplate(
    source_folder: string,
    destination_folder: string,
) {
    return local.error_move_email_s[DEFAULT_LANGUAGE].replace(
        "{source_folder}",
        source_folder,
    ).replace("{destination_folder}", destination_folder);
}

export function getErrorSearhCopiedEmailTemplate(destination_folder: string) {
    return local.error_search_copied_email[DEFAULT_LANGUAGE].replace(
        "{destination_folder}",
        destination_folder,
    );
}

export function getErrorSearhMovedEmailTemplate(destination_folder: string) {
    return local.error_search_moved_email[DEFAULT_LANGUAGE].replace(
        "{destination_folder}",
        destination_folder,
    );
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content/Mailbox.svelte
 * ----------------------------------------------------------------------------
 */
export function getRangePaginationTemplate(
    offset_start: string | number,
    offset_end: string | number,
    total: string | number,
) {
    return local.current_mailbox_offset[DEFAULT_LANGUAGE].replace(
        "{offset_start}",
        String(offset_start),
    )
        .replace("{offset_end}", String(offset_end))
        .replace("{total}", String(total));
}

export function getMailboxSelectionInfoTemplate(
    selection_count: string | number,
) {
    return local.x_count_email_selected[DEFAULT_LANGUAGE].replace(
        "{selection_count}",
        String(selection_count),
    );
}

export function getMailboxSelectAllTemplate(total: string | number) {
    return local.select_all_emails_in_mailbox[DEFAULT_LANGUAGE].replace(
        "{total}",
        String(total),
    );
}

export function getMailboxClearSelectionTemplate() {
    return local.clear_selection[DEFAULT_LANGUAGE];
}

export function getEmptyTrashTemplate(total: string | number) {
    return local.trash_contains[DEFAULT_LANGUAGE].replace(
        "{total}",
        String(total),
    );
}

export function getEmailsMarkedTemplate(mark: string) {
    return local.email_s_marked[DEFAULT_LANGUAGE].replace("{mark}", mark);
}

export function getEmailsUnmarkedTemplate(mark: string) {
    return local.email_s_unmarked[DEFAULT_LANGUAGE].replace("{mark}", mark);
}
