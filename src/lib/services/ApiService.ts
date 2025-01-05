import type { Account, EmailWithContent, Mailbox, OpenMailTaskResults } from "$lib/types";

export enum GetRoutes {
    HELLO = "/hello",
    GET_ACCOUNTS = "/get-accounts",
    GET_MAILBOXES = "/get-mailboxes",
    PAGINATE_MAILBOXES = "/paginate-mailboxes",
    GET_FOLDERS = "/get-folders",
    GET_EMAIL_CONTENT = "/get-email-content",
    GET_PUBLIC_KEY = "/get-public-key",
}

export enum PostRoutes {
    ADD_ACCOUNT = "/add-account",
    EDIT_ACCOUNT = "/edit-account",
    REMOVE_ACCOUNT = "/remove-account",
    REMOVE_ACCOUNTS = "/remove-accounts",
    SEND_EMAIL = "/send-email",
    REPLY_EMAIL = "/reply-email",
    FORWARD_EMAIL = "/forward-email",
    MARK_EMAIL = "/mark-email",
    UNMARK_EMAIL = "/unmark-email",
    MOVE_EMAIL = "/move-email",
    COPY_EMAIL = "/copy-email",
    DELETE_EMAIL = "/delete-email",
    CREATE_FOLDER = "/create-folder",
    RENAME_FOLDER = "/rename-folder",
    MOVE_FOLDER = "/move-folder",
    DELETE_FOLDER = "/delete-folder",
    RESET_FILE_SYSTEM = "/reset-file-system",
    RECREATE_WHOLE_UNIVERSE = "/recreate-whole-universe",
}

interface PostBody {
    [PostRoutes.ADD_ACCOUNT]: {
        email_address: string
        encrypted_password: string
        fullname: string
    };
    [PostRoutes.EDIT_ACCOUNT]: {
        email_address: string
        encrypted_password: string
        fullname: string
    };
    [PostRoutes.REMOVE_ACCOUNT]: {
        account: string
    };
    [PostRoutes.REMOVE_ACCOUNTS]: {};
    [PostRoutes.SEND_EMAIL]: {
        sender: [string, string] | string
        receiver: string
        subject: string
        body: string
        uid?: string
        cc?: string
        bcc?: string
        attachments?: File[]
    };
    [PostRoutes.REPLY_EMAIL]: PostBody[PostRoutes.SEND_EMAIL];
    [PostRoutes.FORWARD_EMAIL]: PostBody[PostRoutes.SEND_EMAIL];
    [PostRoutes.MARK_EMAIL]: {
        account: string
        mark: string
        sequence_set: string
        folder?: string
    };
    [PostRoutes.UNMARK_EMAIL]: {
        account: string
        mark: string
        sequence_set: string
        folder?: string
    };
    [PostRoutes.MOVE_EMAIL]: {
        account: string
        source_folder: string
        destination_folder: string
        sequence_set: string
    };
    [PostRoutes.COPY_EMAIL]: {
        account: string
        source_folder: string
        destination_folder: string
        sequence_set: string
    };
    [PostRoutes.DELETE_EMAIL]: {
        account: string
        folder: string
        sequence_set: string
    };
    [PostRoutes.CREATE_FOLDER]: {
        account: string
        folder_name: string
        parent_folder?: string
    };
    [PostRoutes.RENAME_FOLDER]: {
        account: string
        folder_name: string
        new_folder_name: string
    };
    [PostRoutes.MOVE_FOLDER]: {
        account: string
        folder_name: string
        destination_folder: string
    };
    [PostRoutes.DELETE_FOLDER]: {
        account: string
        folder_name: string
    };
    [PostRoutes.RESET_FILE_SYSTEM]: {};
    [PostRoutes.RECREATE_WHOLE_UNIVERSE]: {};
}

interface GetQueryParams {
    [GetRoutes.HELLO]: {};
    [GetRoutes.GET_ACCOUNTS]: {};
    [GetRoutes.GET_MAILBOXES]: {
        pathParams: {
            accounts: string
        }
        queryParams?: {
            folder?: string;
            search?: string;
            offset_start?: number;
            offset_end?: number;
        }
    };
    [GetRoutes.PAGINATE_MAILBOXES]: {
        pathParams: {
            accounts: string
            offset_start: number;
            offset_end: number;
        }
    };
    [GetRoutes.GET_FOLDERS]: {
        pathParams: {
            accounts: string;
        }
    };
    [GetRoutes.GET_EMAIL_CONTENT]: {
        pathParams: {
            accounts: string;
            folder: string;
            uid: string;
        }
    };
    [GetRoutes.GET_PUBLIC_KEY]: {};
}

export interface GetQueryResponse {
    [GetRoutes.HELLO]: {},
    [GetRoutes.GET_ACCOUNTS]: {
        connected: Account[];
        failed: Account[];
    },
    [GetRoutes.GET_MAILBOXES]: OpenMailTaskResults<Mailbox>,
    [GetRoutes.PAGINATE_MAILBOXES]: OpenMailTaskResults<Mailbox>,
    [GetRoutes.GET_FOLDERS]: OpenMailTaskResults<string[]>,
    [GetRoutes.GET_EMAIL_CONTENT]: EmailWithContent,
    [GetRoutes.GET_PUBLIC_KEY]: {
        public_key: string;
    }
}

export type GetResponse<T extends GetRoutes> = {
    success: boolean;
    message: string;
    data?: GetQueryResponse[T];
}

export type PostResponse = {
    success: boolean;
    message: string;
}

export class ApiService {
    static _removeUndefinedParams(
        params: Record<string, any | undefined>
    ): Record<string, string> {
        return Object.fromEntries(
            Object.entries(params).filter((entry) => entry[1] !== undefined)
        );
    }

    static async get<T extends GetRoutes>(
        url: string,
        endpoint: T,
        params?: GetQueryParams[T]
    ): Promise<GetResponse<T>> {
        const createQueryString = (params: GetQueryParams[T]) => {
            let queryString = "";

            if(params && "pathParams" in params && params.pathParams)
                queryString += "/" + Object.values(params.pathParams).join("/")

            if(params && "queryParams" in params && params.queryParams)
                queryString += "?" + new URLSearchParams(
                    ApiService._removeUndefinedParams(params.queryParams)
                ).toString()

            return queryString
        }

        const queryString = params ? createQueryString(params) : "";
        const response = await fetch(url + endpoint + queryString);
        return response.json();
    }

    static async post<T extends PostRoutes>(
        url: string,
        endpoint: T,
        body: PostBody[T] | FormData
    ): Promise<PostResponse> {
        const response = await fetch(url + endpoint, {
            method: "POST",
            headers: body instanceof FormData
                ? {}
                : { "Content-Type": "application/json" },
            body: body instanceof FormData
                ? body
                : JSON.stringify(
                    this._removeUndefinedParams(body)
                ),
        });

        return response.json();
    }
}
