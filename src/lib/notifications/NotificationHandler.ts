import {
    isPermissionGranted,
    requestPermission,
    sendNotification,
} from "@tauri-apps/plugin-notification";
import { SharedStore } from "$lib/stores/shared.svelte";
import { type Account, type Email, Folder, type INotificationHandler } from "$lib/types";
import { DEFAULT_LANGUAGE } from "$lib/constants";
import { local } from "$lib/locales";
import { isStandardFolder } from "$lib/utils";
import { MailboxController } from "$lib/mailbox";

export class NotificationHandler implements INotificationHandler {
    private _permissionGranted: boolean;
    private _account: Account;
    private _ws: WebSocket | undefined;

    public constructor(account: Account) {
        this._account = account;
        this._permissionGranted = false;
        this._ws = undefined;
        // TODO: Open this later.
        //this.initialize();
    }

    public get account() {
        return this._account;
    }

    public set account(account: Account) {
        this._account = account;
        this.terminate();
        this.initialize();
    }

    public areNotificationsAllowed() {
        return this._permissionGranted;
    }

    private async _checkForPermissions() {
        this._permissionGranted = await isPermissionGranted();
        if (!this._permissionGranted) {
            const permission = await requestPermission();
            this._permissionGranted = permission === "granted";
        }
    }

    private _addMessageIntoInbox(emailAddr: string, recentEmails: Email[]) {
        // If the current mailbox is not the owner of the incoming messages,
        // we can skip this.
        if (
            !Object.hasOwn(SharedStore.mailboxes, emailAddr) ||
            !isStandardFolder(
                SharedStore.mailboxes[emailAddr].folder,
                Folder.Inbox,
            )
        ) return;

        const targetMailbox = SharedStore.mailboxes[emailAddr].emails;

        // Add email summary of recent email to the top of the current
        const recentEmailsLength = recentEmails.length;
        targetMailbox.current.unshift(...recentEmails);

        // and shift emails that are overflowed from current to next.
        const overflowEmails = targetMailbox.current.splice(-1 * recentEmailsLength);
        targetMailbox.next.unshift(...overflowEmails);

        // Delete emails those are overflowed from next.
        targetMailbox.next.splice(-1 * recentEmailsLength, recentEmailsLength);
    }

    private _addMessageIntoOwnerChannel(emailAddr: string, recentEmails: Email[]) {
        if (!Object.hasOwn(SharedStore.recentEmailsChannel, emailAddr))
            return;

        // Fetch email content of recent email and add it into recentEmailsChannel.
        const targetAccount = SharedStore.accounts.find(
            (account) => account.email_address === emailAddr,
        )!
        if (!targetAccount) return;

        for (const recentEmail of recentEmails) {
            MailboxController
                .getEmailContent(targetAccount, Folder.Inbox, recentEmail.uid)
                .then((response) => {
                    if (!response.success || !response.data) return;
                    SharedStore.recentEmailsChannel[emailAddr].push(response.data);
                });
        }
    }

    private _handleIncomingEmailMessages(emailAddr: string, recentEmails: Email[]) {
        this._addMessageIntoInbox(emailAddr, recentEmails);
        this._addMessageIntoOwnerChannel(emailAddr, recentEmails);
    }

    public pushDesktopNotification(title?: string, body?: string) {
        if (this.areNotificationsAllowed()) {
            sendNotification({
                title: title || local.new_email_received_title[DEFAULT_LANGUAGE],
                body: body || local.new_email_received_body[DEFAULT_LANGUAGE],
            });
        }
    }

    private _setupWebSocketChannel() {
        this._checkForPermissions();
        SharedStore.recentEmailsChannel[this.account.email_address] = [];
    }

    private _listenForNewMessages(e: MessageEvent<typeof SharedStore.recentEmailsChannel>) {
        const recentMessages = e.data;
        this.pushDesktopNotification();
        Object.entries(recentMessages).forEach(
            ([ emailAddr, recentEmails ]) => {
                return this._handleIncomingEmailMessages(
                    emailAddr,
                    recentEmails
                );
            }
        );
    }

    private _handleWebSocketClose(e: CloseEvent) {
        if (e.reason && e.reason.toLowerCase().includes("error")) {
            console.error(e.reason);
        }
    }

    public terminate() {
        if (!this._ws) return;
        this._ws.close();
    }

    public initialize() {
        if (this._ws)
            return;

        this._ws = new WebSocket(
            SharedStore.server.replace("http", "ws") +
                `/notifications/${this.account}`,
        );

        this._ws.addEventListener("open", this._setupWebSocketChannel)
        this._ws.addEventListener("message", this._listenForNewMessages);
        this._ws.addEventListener("close", this._handleWebSocketClose);
    }

    public reinitialize() {
        if (this._ws)
            this.terminate();
        this.initialize();
    }
}
