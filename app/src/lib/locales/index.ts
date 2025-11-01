import { Language } from "$lib/preferences";
import { SharedStore } from "$lib/stores/shared.svelte";

export const local = {
    feature_not_implemented: {
        en: "{feature} feature does not implemented yet",
    },
    failed_accounts_are: {
        en: "Failed accounts are:",
    },
    accounts_of_failed_mailboxes_are: {
        en: "Accounts of failed mailboxes are:",
    },
    accounts_of_failed_folders_are: {
        en: "Accounts of failed folders are:",
    },
    on_wrote: {
        en: "On {original_date}, {original_sender} wrote:",
    },
    forwarded_message: {
        en: "---------- Forwarded message ----------",
    },
    from: {
        en: "From",
    },
    date: {
        en: "Date",
    },
    subject: {
        en: "Subject",
    },
    to: {
        en: "To",
    },
    sender_to_receiver: {
        en: "{sender_fullname} <a>&lt;{sender_email}&gt;</a> to {receiver_fullname} <a>&lt;{receiver_email}&gt;</a> at {sent_at}",
    },
    sender_to_receiver_and_others: {
        en: `{sender_fullname} <a>&lt;{sender_email}&gt;</a> to {receiver_fullname} <a>&lt;{receiver_email}&gt;</a> and <u class="others">others</u> at {sent_at}`,
    },
    current_email_offset: {
        en: "{current} of {total}",
    },
    current_mailbox_offset: {
        en: "{offset_start} - {offset_end} of {total}",
    },
    x_count_email_selected: {
        en: "<b>{selection_count}</b> emails in this page selected.",
    },
    select_all_emails_in_mailbox: {
        en: "Select all &nbsp;<b>{total}</b>&nbsp; emails in this page.",
    },
    clear_selection: {
        en: "Clear selection",
    },
    sender_to_receiver_of_new_message: {
        en: `{sender_fullname} <a class="sender-email">&lt;{sender_email}&gt;</a> to <a class="receiver-email">&lt;{receiver_email}&gt;</a> at {sent_at}`,
    },
    no_match_found: {
        en: "No matching options found",
    },
    undo: {
        en: "Undo",
    },
    search: {
        en: "Search",
    },
    close: {
        en: "Close",
    },
    password: {
        en: "Password",
    },
    upload_file: {
        en: "Upload a file.",
    },
    drop_files_here: {
        en: "or drop files here",
    },
    remove: {
        en: "Remove",
    },
    january: {
        en: "January",
    },
    february: {
        en: "February",
    },
    march: {
        en: "March",
    },
    april: {
        en: "April",
    },
    may: {
        en: "May",
    },
    june: {
        en: "June",
    },
    july: {
        en: "July",
    },
    august: {
        en: "August",
    },
    september: {
        en: "September",
    },
    october: {
        en: "October",
    },
    november: {
        en: "November",
    },
    december: {
        en: "December",
    },
    sun: {
        en: "Sun",
    },
    mon: {
        en: "Mon",
    },
    tue: {
        en: "Tue",
    },
    wed: {
        en: "Wed",
    },
    thu: {
        en: "Thu",
    },
    fri: {
        en: "Fri",
    },
    sat: {
        en: "Sat",
    },
    cancel: {
        en: "Cancel",
    },
    manage: {
        en: "Manage",
    },
    loading: {
        en: "Loading",
    },
    openmail: {
        en: "Openmail",
    },
    secure_and_fast_email_client: {
        en: "Secure, Private and Fast Email Client",
    },
    connecting_to_accounts: {
        en: "Connecting to accounts...",
    },
    email_address: {
        en: "Email Address",
    },
    email_address_example: {
        en: "alexdoe@mail.com",
    },
    full_name_optional: {
        en: "Full Name (Optional)",
    },
    full_name_example: {
        en: "Example: Alex Doe <alex.doe@openmail.com>",
    },
    full_name_placeholder: {
        en: "Alex Doe",
    },
    connect_to_account: {
        en: "Connect to account",
    },
    error_add_account: {
        en: "Something went wrong while adding account.",
    },
    error_edit_account: {
        en: "Something went wrong while updating your account.",
    },
    error_remove_account: {
        en: "Something went wrong while removing your account.",
    },
    error_remove_all_account: {
        en: "Something went wrong while removing accounts.",
    },
    error_initialize_accounts: {
        en: "Something went wrong while loading accounts. Please check your account list.",
    },
    error_initialize_mailboxes: {
        en: "Something went wrong while loading mailboxes. Please try restarting the app.",
    },
    error_failed_mailboxes_or_folders: {
        en: "Something went wrong while loading mailboxes and/or folders.",
    },
    error_search_emails: {
        en: "Something went wrong while searching for emails.",
    },
    error_sent_mailbox_after_sending_emails: {
        en: "Email has sent but something went wrong while loading sent mailbox."
    },
    error_search_copied_email: {
        en: "Copied email could not found in {destination_folder}"
    },
    error_search_moved_email: {
        en: "Moved email could not found in {destination_folder}"
    },
    error_get_mailbox: {
        en: "Something went wrong while loading mailbox.",
    },
    error_refresh_folders: {
        en: "Something went wrong while refreshing folders.",
    },
    error_refresh_mailbox_s: {
        en: "Something went wrong while refreshing one or more mailboxes.",
    },
    error_show_home: {
        en: "Something went wrong while loading inboxes.",
    },
    error_get_email_content: {
        en: "Something went wrong while loading email content.",
    },
    error_not_logged_out_account: {
        en: "Something went wront while logging out from {account}."
    },
    error_create_folder: {
        en: "Something went wrong while creating folder."
    },
    error_delete_folder: {
        en: "Something went wrong while deleting folder."
    },
    error_rename_folder: {
        en: "Something went wrong while renaming folder."
    },
    error_move_folder: {
        en: "Something went wrong while moving folder."
    },
    error_save_email_s_as_draft: {
        en: "Something went wrong while saving email(s) as draft.",
    },
    error_send_email_s: {
        en: "Something went wrong while sending email(s)."
    },
    error_attachment_download: {
        en: "Something went wrong while downloading attachment. Please try again."
    },
    error_mark_email_s: {
        en: "Something went wrong while marking email(s) as {mark}."
    },
    error_unmark_email_s: {
        en: "Something went wrong while unmarking email(s) as {mark}"
    },
    error_copy_email_s: {
        en: "Something went wrong while copying email(s) from {source_folder} to {destination_folder}"
    },
    error_move_email_s: {
        en: "Something went wrong while moving email(s) from {source_folder} to {destination_folder}"
    },
    error_delete_email_s: {
        en: "Something went wrong while deleting email(s)"
    },
    error_unsubscribe_s: {
        en: "Something went wrong while unsubscribing from newsletter(s)."
    },
    error_empty_trash: {
        en: "Something went wrong while emptying the trash."
    },
    at_least_one_receiver: {
        en: "At least one receiver must be added"
    },
    are_you_certain_remove_account: {
        en: "Are you certain? Removing an account cannot be undone.",
    },
    are_you_certain_remove_all_accounts: {
        en: "Are you certain? You are about to remove all accounts, this action cannot be undone.",
    },
    are_you_certain_log_out: {
        en: "Are you sure you want to log out? You will need to sign in again to access your account",
    },
    are_you_certain_delete_email: {
        en: "Are you certain? Deleting an email cannot be undone"
    },
    are_you_certain_delete_email_s: {
        en: "Are you certain? Deleting email(s) cannot be undone",
    },
    are_you_certain_quit_app: {
        en: "Are you sure you want to close the application? Any unsaved changes will be lost.",
    },
    are_you_certain_subject_is_empty: {
        en: "The subject field is empty. Are you sure you want to send the email without a subject?"
    },
    are_you_certain_body_is_empty: {
        en: "The message body is empty. Are you sure you want to send the email without any content?"
    },
    which_accounts_added: {
        en: "Which accounts have I added?",
    },
    add_another_account: {
        en: "I want to add another account.",
    },
    continue_to_mailbox: {
        en: "Continue to mailbox.",
    },
    edit: {
        en: "Edit",
    },
    warning: {
        en: "Warning",
    },
    remove_all: {
        en: "Remove All",
    },
    account_selected: {
        en: `Account ({count} selected)`,
    },
    accounts_failed_to_connect: {
        en: `There were one or more accounts that failed to connect.`,
    },
    new_email_received_title: {
        en: "New Email Received!",
    },
    new_email_received_body: {
        en: "Here, look at your new email.",
    },
    exit: {
        en: "Exit",
    },
    restart_app: {
        en: "Restart the App",
    },
    yes_remove_all: {
        en: "Yes, remove all.",
    },
    yes_delete: {
        en: "Yes, delete."
    },
    yes_remove: {
        en: "Yes, remove.",
    },
    retry: {
        en: "Retry",
    },
    account: {
        en: "Account",
    },
    search_for_account: {
        en: "Search for {account}",
    },
    searching_account: {
        en: "Searching Account",
    },
    home: {
        en: "Home",
    },
    folder: {
        en: "Folder",
    },
    sender_s: {
        en: "Sender(s)",
    },
    receiver_s: {
        en: "Receiver(s)",
    },
    cc: {
        en: "Cc",
    },
    bcc: {
        en: "Bcc",
    },
    subject_placeholder: {
        en: "For example: Project Proposal, Meeting Notes",
    },
    add_email_address_with_space_placeholder: {
        en: "Enter someone@mail.com then press 'Space'",
    },
    date_range: {
        en: "Date Range",
    },
    since: {
        en: "Since",
    },
    before: {
        en: "Before",
    },
    includes: {
        en: "Includes",
    },
    includes_placeholder: {
        en: "Words to include in search...",
    },
    excludes: {
        en: "Excludes",
    },
    excludes_placeholder: {
        en: "Words to exclude from search...",
    },
    flags: {
        en: "Flags",
    },
    included_flags: {
        en: "Included Flags",
    },
    excluded_flags: {
        en: "Excluded Flags",
    },
    size: {
        en: "Size",
    },
    larger_than: {
        en: "Larger Than",
    },
    larger_than_placeholder: {
        en: "1",
    },
    smaller_than: {
        en: "Smaller Than",
    },
    smaller_than_placeholder: {
        en: "1",
    },
    has_attachments: {
        en: "Has attachments",
    },
    clear: {
        en: "Clear",
    },
    go_to_home: {
        en: "Go to Home",
    },
    notifications: {
        en: "Notifications",
    },
    refresh_folders: {
        en: "Refresh",
    },
    create_folder: {
        en: "Create",
    },
    create_subfolder: {
        en: "Create Subfolder",
    },
    rename_folder: {
        en: "Rename Folder",
    },
    move_folder: {
        en: "Move Folder",
    },
    delete_folder: {
        en: "Delete Folder",
    },
    minimize_to_tray: {
        en: "Minimize"
    },
    settings: {
        en: "Settings"
    },
    logout_from_account: {
        en: "Logout from {account}"
    },
    quit: {
        en: "Quit"
    },
    yes_close_the_app: {
        en: "Yes, close the app."
    },
    yes_logout: {
        en: "Yes, logout."
    },
    create: {
        en: "Create"
    },
    folder_name: {
        en: "Folder Name"
    },
    new_folder_placeholde: {
        en: "My New Folder"
    },
    parent_folder: {
        en: "Parent Folder"
    },
    select_parent_folder: {
        en: "Select Parent Folder"
    },
    delete: {
        en: "Delete"
    },
    delete_subfolders: {
        en: "Delete Subfolders"
    },
    rename: {
        en: "Rename"
    },
    new_folder_name: {
        en: "New Folder Name"
    },
    move: {
        en: "Move"
    },
    destination_folder: {
        en: "Destination Folder"
    },
    select_folder: {
        en: "Select Folder"
    },
    yes_send: {
        en: "Yes, send."
    },
    body: {
        en: "Body"
    },
    attachment_s: {
        en: "Attachment(s)"
    },
    send_email: {
        en: "Send Email"
    },
    save_as_draft: {
        en: "Save as Draft"
    },
    back: {
        en: "Back"
    },
    star: {
        en: "Star"
    },
    remove_star: {
        en: "Remove Star"
    },
    mark_as_read: {
        en: "Mark as Read"
    },
    mark_as_unread: {
        en: "Mark as Unread"
    },
    move_to_inbox: {
        en: "Move to Inbox"
    },
    move_to_archive: {
        en: "Move to Archive"
    },
    reply: {
        en: "Reply"
    },
    forward: {
        en: "Forward"
    },
    print: {
        en: "Print"
    },
    spam: {
        en: "Spam"
    },
    view_source: {
        en: "View Source"
    },
    unsubscribe: {
        en: "Unsubscribe"
    },
    copy_to: {
        en: "Copy To"
    },
    move_to: {
        en: "Move To"
    },
    next: {
        en: "Next"
    },
    prev: {
        en: "Prev"
    },
    new: {
        en: "New"
    },
    today: {
        en: "Today"
    },
    yesterday: {
        en: "Yesterday"
    },
    this_week: {
        en: "This Week"
    },
    this_month: {
        en: "This Month"
    },
    older: {
        en: "Older"
    },
    unsubscribe_all: {
        en: "Unsubscribe All"
    },
    refresh: {
        en: "Refresh"
    },
    empty_trash: {
        en: "Empty Trash"
    },
    trash_contains: {
        en: "The trash contains {total} email(s) in total."
    },
    dismiss: {
        en: "Dismiss"
    },
    manage_accounts: {
        en: "Manage Accounts"
    },
    delete_completely: {
        en: "Delete Completely"
    },
    email_s_marked: {
        en: "Email(s) marked as {mark}."
    },
    email_s_unmarked: {
        en: "{mark} mark removed from Email(s)."
    },
    undo_done: {
        en: "Operation undone."
    },
    server_url: {
        en: "Server URL",
    },
    server_url_example: {
        en: "http://127.0.0.1:8000",
    },
    error_change_server_url: {
        en: "Could not change server url"
    }
};

/*
const locales = {
    welcome: {
        [Language.EN_US]: "welcome",
    },
    hello: {
        [Language.EN_US]: (name: string) => `${local.welcome} {name}`.replace("{name}", name),
    }
} as const;

type Locales = typeof locales;

type Localized<T, L extends Language> = {
    [K in keyof T]: T[K] extends Record<L, infer R> ? R : never;
};

export const local = new Proxy({} as Localized<Locales, Language>, {
    get(_target, prop: string | symbol) {
        if (typeof prop === "string" && locales[prop as keyof Locales]) {
            const value = locales[prop as keyof Locales][SharedStore.preferences.language];
            return value;
        }
        return undefined;
    }
});

// Usage
console.log(local.welcome); // "welcome"
console.log(local.hello("alex")); // "welcome alex"
*/
