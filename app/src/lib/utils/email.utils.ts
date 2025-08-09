import { type Account } from "$lib/types";
import { pulseTarget } from ".";

export function isEmailValid(email: string): boolean {
    return (
        email.match(/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/) !== null
    );
}

export function createSenderAddress(
    emailAddress: string,
    fullname: string | null = null,
): string {
    if (fullname && fullname.length > 0) return `${fullname} <${emailAddress}>`;
    return emailAddress;
}

export function createSenderAddressFromAccount(account: Account): string {
    return createSenderAddress(account.email_address, account.fullname);
}

export function extractFullname(sender: string): string {
    const match = sender.match(/^(.*?)<.*@.*>$/);
    return match ? match[1].trim() : "";
}

export function extractEmailAddress(sender: string): string {
    const match = sender.match(/<(.+@.+)>/);
    if (match) return match[1].trim();
    return sender.includes("@") ? sender.trim() : "";
}

export function addEmailToAddressList(
    e: Event,
    input: HTMLInputElement,
    addressList: string[],
) {
    if (e instanceof KeyboardEvent && (e.key === " " || e.key === "Spacebar")) {
        e.preventDefault();
    } else if (!(e instanceof FocusEvent || e instanceof MouseEvent)) {
        return;
    }

    const trimmedValue = input.value.trim();
    if (trimmedValue.length <= 0) return;

    if (!isEmailValid(extractEmailAddress(trimmedValue))) {
        pulseTarget(input);
        return;
    }

    addressList.push(trimmedValue);
    input.value = "";
}
