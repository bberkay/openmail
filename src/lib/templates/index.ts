/**
 * ----------------------------------------------------------------------------
 * Generally used constants
 * ----------------------------------------------------------------------------
 */
export function getNotImplementedTemplate(feature: string) {
    return `{feature} feature does not implemented yet`.replace(
        "{feature}",
        feature,
    );
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Landing/Register/AccountList.svelte
 * ----------------------------------------------------------------------------
 */
export function getFailedAccountTemplate(failed_account_list_items: string) {
    return `
    <p>Failed accounts are:</p>
    <ul>
        {failed_account_list_items}
    </ul>
    `.replace("{failed_account_list_items}", failed_account_list_items);
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
     <p>Accounts of failed mailboxes are:</p>
     <ul>
        {failed_mailbox_list_items}
     </ul>
     <p>Accounts of failed folders are:</p>
     <ul>
        {failed_folder_list_items}
     </ul>
     `
        .replace("{failed_mailbox_list_items}", failed_mailbox_list_items)
        .replace("{failed_folder_list_items}", failed_folder_list_items);
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
        On {original_date}, {original_sender} wrote:<br/>
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
        ---------- Forwarded message ----------<br/>
        From: {original_sender}<br/>
        Date: {original_date}<br/>
        Subject: {original_subject}<br/>
        To: {original_receivers}<br/>
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
    return `
    {sender_fullname} <a>&lt;{sender_email}&gt;</a> to {receiver_email} at {sent_at}
    `
        .replace("{sender_fullname}", sender_fullname)
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
    return `
    {sender_fullname} <a>&lt;{sender_email}&gt;</a> to {receiver_email} and <u class="others">others</u> at {sent_at}
    `
        .replace("{sender_fullname}", sender_fullname)
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
    return `
    {current} of {total}
    `
        .replace("{current}", String(current))
        .replace("{total}", String(total));
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content/Inbox.svelte
 * ----------------------------------------------------------------------------
 */
export function getMailboxPaginationTemplate(
    offset_start: string | number,
    offset_end: string | number,
    total: string | number,
) {
    return `
    {offset_start} - {offset_end} of {total}
    `
        .replace("{offset_start}", String(offset_start))
        .replace("{offset_end}", String(offset_end))
        .replace("{total}", String(total));
}

export function getMailboxSelectionInfoTemplate(
    selection_count: string | number,
) {
    return `
    <b>{selection_count}</b> emails in this page selected.
    `.replace("{selection_count}", String(selection_count));
}

export function getMailboxSelectAllTemplate(total: string | number) {
    return `
    Select all <b>{total}</b> emails in this page.
    `.replace("{total}", String(total));
}

export function getMailboxClearSelectionTemplate() {
    return `
    Clear selection
    `;
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
    return `
    {sender_fullname} <a class="sender-email">&lt;{sender_email}&gt;</a> to <a class="receiver-email">&lt;{receiver_email}&gt;</a> at {sent_at}
    `
        .replace("{sender_fullname}", sender_fullname)
        .replace("{sender_email}", sender_email)
        .replace("{receiver_email}", receiver_email)
        .replace("{sent_at}", sent_at);
}

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Components/Select/Select.svelte
 * ----------------------------------------------------------------------------
 */
export function getNoMatchFoundTemplate() {
    return `
    <div class="no-results">No matching options found</div>
    `;
}
