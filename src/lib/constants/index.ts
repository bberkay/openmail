/**
 * ----------------------------------------------------------------------------
 * Generally used constants
 * ----------------------------------------------------------------------------
 */
export const NOT_IMPLEMENTED_TEMPLATE = `
    {feature} feature does not implemented yet.
`

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content/Compose.svelte
 * ----------------------------------------------------------------------------
 */
export const REPLY_TEMPLATE = `
    <br/><br/>
    <div>
        On {original_date}, {original_sender} wrote:<br/>
        <blockquote style="margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex">
            {original_body}
        </blockquote>
    </div>
`;

export const FORWARD_TEMPLATE = `
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
`;

export const SENDER_TO_RECEIVER_TEMPLATE = `
    {sender_fullname} <a>&lt;{sender_email}&gt;</a> to {receiver_email} at {sent_at}
`;

export const SENDER_TO_RECEIVER_AND_OTHERS_TEMPLATE = `
    {sender_fullname} <a>&lt;{sender_email}&gt;</a> to {receiver_email} and <u class="others">others</u> at {sent_at}
`;

export const ATTACHMENT_TEMPLATE = `
    {attachment_name} ({attachment_size})
`;

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content/Email.svelte
 * ----------------------------------------------------------------------------
 */
export const EMAIL_PAGINATION_TEMPLATE = `
    {current} of {total}
`;

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Content/Inbox.svelte
 * ----------------------------------------------------------------------------
 */
export const MAILBOX_LENGTH = 10;

export const MAILBOX_PAGINATION_TEMPLATE = `
    {offset_start} - {offset_end} of {total}
`;

export const MAILBOX_SELECTION_INFO_TEMPLATE = `
    <b>{selection_count}</b> emails in this page selected.
`;

export const MAILBOX_SELECT_ALL_TEMPLATE = `
    Select all <b>{total}</b> emails in this page.
`;

export const MAILBOX_CLEAR_SELECTION_TEMPLATE = `
    Clear selection
`;

/**
 * ----------------------------------------------------------------------------
 * Constants generally used in Main/Navbar/Notifications.svelte
 * ----------------------------------------------------------------------------
 */
export const NEW_MESSAGE_TEMPLATE = `
    {sender_fullname} <a class="sender-email">&lt;{sender_email}&gt;</a> to <a class="receiver-email">&lt;{receiver_email}&gt;</a> at {sent_at}
`;
