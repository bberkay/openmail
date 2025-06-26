import { NotificationHandler } from "$lib/handlers/NotificationHandler";
import type { Account, INotificationHandler, OpenmailTaskResults } from "$lib/types";

let notificationChannels: OpenmailTaskResults<INotificationHandler> = {};

export class NotificationManager {
    public static hasChannel(email_address: string): boolean {
        return Object.hasOwn(notificationChannels, email_address);
    }

    public static create(account: Account) {
        if (!NotificationManager.hasChannel(account.email_address)) {
            notificationChannels[account.email_address] = new NotificationHandler(account);
        } else {
            notificationChannels[account.email_address].reinitialize();
        }
    }

    public static terminate(account: Account) {
        if (!NotificationManager.hasChannel(account.email_address)) return;
        notificationChannels[account.email_address].terminate();
        delete notificationChannels[account.email_address];
    }

    public static terminateAll() {
        Object.values(notificationChannels).forEach(ch => ch.terminate());
        notificationChannels = {};
    }
}
