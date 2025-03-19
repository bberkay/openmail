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
    {sender_fullname} <a>&lt;{sender_email}&gt;</a> to You and <u>others</u> at {sent_at}
`;

export const ATTACHMENT_TEMPLATE = `
    {attachment_name} ({attachment_size})
`;
