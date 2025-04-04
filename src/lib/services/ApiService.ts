import type {
    Account,
    Attachment,
    Email,
    Draft,
    PMailbox,
    OpenMailTaskResults,
} from "$lib/types";
import { removeFalsyParamsAndEmptyLists } from "$lib/utils";

export enum GetRoutes {
    HELLO = "/hello",
    GET_ACCOUNTS = "/get-accounts",
    GET_MAILBOX = "/get-mailbox",
    PAGINATE_MAILBOX = "/paginate-mailbox",
    GET_FOLDERS = "/get-folders",
    GET_EMAIL_CONTENT = "/get-email-content",
    DOWNLOAD_ATTACHMENT = "/download-attachment",
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
    SAVE_EMAIL_AS_DRAFT = "/save-email-as-draft",
    MARK_EMAIL = "/mark-email",
    UNMARK_EMAIL = "/unmark-email",
    MOVE_EMAIL = "/move-email",
    COPY_EMAIL = "/copy-email",
    DELETE_EMAIL = "/delete-email",
    CREATE_FOLDER = "/create-folder",
    RENAME_FOLDER = "/rename-folder",
    MOVE_FOLDER = "/move-folder",
    DELETE_FOLDER = "/delete-folder",
}

interface QueryParams {
    [GetRoutes.HELLO]: {};
    [GetRoutes.GET_ACCOUNTS]: {};
    [GetRoutes.GET_MAILBOX]: {
        pathParams: {
            account: string;
        };
        queryParams?: {
            folder?: string;
            search?: string;
            offset_start?: number;
            offset_end?: number;
        };
    };
    [GetRoutes.PAGINATE_MAILBOX]: {
        pathParams: {
            account: string;
            offset_start?: number;
            offset_end?: number;
        };
    };
    [GetRoutes.GET_FOLDERS]: {
        pathParams: {
            accounts: string;
        };
    };
    [GetRoutes.GET_EMAIL_CONTENT]: {
        pathParams: {
            account: string;
            folder: string;
            uid: string;
        };
    };
    [GetRoutes.DOWNLOAD_ATTACHMENT]: {
        pathParams: {
            account: string;
            folder: string;
            uid: string;
            name: string;
        };
        queryParams?: {
            cid?: string;
        }
    };
    [GetRoutes.GET_PUBLIC_KEY]: {};
    [PostRoutes.REPLY_EMAIL]: {
        pathParams: {
            original_message_id: string;
        }
    };
    [PostRoutes.FORWARD_EMAIL]: {
        pathParams: {
            original_message_id: string;
        }
    }
    [key: string]: any;
}

interface PostBody {
    [PostRoutes.ADD_ACCOUNT]: {
        email_address: string;
        encrypted_password: string;
        fullname?: string;
    };
    [PostRoutes.EDIT_ACCOUNT]: {
        email_address: string;
        encrypted_password: string;
        fullname?: string;
    };
    [PostRoutes.REMOVE_ACCOUNT]: {
        account: string;
    };
    [PostRoutes.REMOVE_ACCOUNTS]: {};
    [PostRoutes.SEND_EMAIL]: FormData | Draft;
    [PostRoutes.REPLY_EMAIL]: PostBody[PostRoutes.SEND_EMAIL];
    [PostRoutes.FORWARD_EMAIL]: PostBody[PostRoutes.SEND_EMAIL];
    [PostRoutes.SAVE_EMAIL_AS_DRAFT]: {
        email: PostBody[PostRoutes.SEND_EMAIL],
        appenduid?: string
    };
    [PostRoutes.MARK_EMAIL]: {
        account: string;
        mark: string;
        sequence_set: string;
        folder?: string;
    };
    [PostRoutes.UNMARK_EMAIL]: {
        account: string;
        mark: string;
        sequence_set: string;
        folder?: string;
    };
    [PostRoutes.MOVE_EMAIL]: {
        account: string;
        source_folder: string;
        destination_folder: string;
        sequence_set: string;
    };
    [PostRoutes.COPY_EMAIL]: {
        account: string;
        source_folder: string;
        destination_folder: string;
        sequence_set: string;
    };
    [PostRoutes.DELETE_EMAIL]: {
        account: string;
        folder: string;
        sequence_set: string;
    };
    [PostRoutes.CREATE_FOLDER]: {
        account: string;
        folder_name: string;
        parent_folder?: string;
    };
    [PostRoutes.RENAME_FOLDER]: {
        account: string;
        folder_name: string;
        new_folder_name: string;
    };
    [PostRoutes.MOVE_FOLDER]: {
        account: string;
        folder_name: string;
        destination_folder: string;
    };
    [PostRoutes.DELETE_FOLDER]: {
        account: string;
        folder_name: string;
        delete_subfolders: boolean;
    };
}

export interface BaseResponse {
    success: boolean;
    message: string;
}

export interface GetQueryResponse {
    [GetRoutes.HELLO]: {};
    [GetRoutes.GET_ACCOUNTS]: {
        connected: Account[];
        failed: Account[];
    };
    [GetRoutes.GET_MAILBOX]: OpenMailTaskResults<PMailbox>;
    [GetRoutes.PAGINATE_MAILBOX]: OpenMailTaskResults<PMailbox>;
    [GetRoutes.GET_FOLDERS]: OpenMailTaskResults<string[]>;
    [GetRoutes.GET_EMAIL_CONTENT]: Email;
    [GetRoutes.DOWNLOAD_ATTACHMENT]: Attachment;
    [GetRoutes.GET_PUBLIC_KEY]: { public_key: string };
}

export interface PostQueryResponse {
    [PostRoutes.SAVE_EMAIL_AS_DRAFT]: string; // appenduid
}

export interface GetResponse<T extends GetRoutes> extends BaseResponse {
    data?: GetQueryResponse[T];
}

export interface PostResponse<T extends PostRoutes = PostRoutes> extends BaseResponse {
    data?: T extends keyof PostQueryResponse ? PostQueryResponse[T] : undefined;
}

export class ApiService {
    static createQueryString<T extends GetRoutes | PostRoutes>(params: QueryParams[T]): string {
        let queryString = "";

        if (params && "pathParams" in params && params.pathParams)
            queryString += "/" + Object.values(params.pathParams).join("/");

        if (params && "queryParams" in params && params.queryParams)
            queryString +=
                    "?" +
                    new URLSearchParams(
                        removeFalsyParamsAndEmptyLists(params.queryParams),
                    ).toString();

        return queryString;
    }

    static async get<T extends GetRoutes>(
        url: string,
        endpoint: T,
        params?: QueryParams[T],
    ): Promise<GetResponse<T>> {
        const queryString = params ? ApiService.createQueryString(params) : "";
        const response = await fetch(url + endpoint + queryString);
        const data = await response.json();
        return data
    }

    static async post<T extends PostRoutes>(
        url: string,
        endpoint: T,
        body: PostBody[T],
        params?: QueryParams[T]
    ): Promise<PostResponse<T>> {
        const queryString = params ? ApiService.createQueryString(params) : "";
        const response = await fetch(url + endpoint + queryString, {
            method: "POST",
            headers:
                body instanceof FormData
                    ? {}
                    : { "Content-Type": "application/json" },
            body:
                body instanceof FormData
                    ? body
                    : JSON.stringify(removeFalsyParamsAndEmptyLists(body)),
        });

        const data = await response.json();
        return data
    }
}
