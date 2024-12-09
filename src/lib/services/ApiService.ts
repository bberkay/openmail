export enum GetRoutes {
    HELLO = "/hello",
    GET_EMAIL_ACCOUNTS = "/get-email-accounts",
    GET_EMAILS = "/get-emails",
    PAGINATE_EMAILS = "/paginate-emails",
    GET_FOLDERS = "/get-folders",
    GET_EMAIL_CONTENT = "/get-email-content",
}

export enum PostRoutes {
    ADD_EMAIL_ACCOUNT = "/add-email-account",
    DELETE_EMAIL_ACCOUNT = "/delete-email-account",
    DELETE_EMAIL_ACCOUNTS = "/delete-email-accounts",
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
    REFRESH_WHOLE_UNIVERSE = "/refresh-whole-universe",
}

export type Response = {
    success: boolean;
    message: string;
    data: any;
}

interface GetQueryParams {
    [GetRoutes.HELLO]: {};
    [GetRoutes.GET_EMAIL_ACCOUNTS]: {};
    [GetRoutes.GET_EMAILS]: {
        accounts: string;
        folder?: string;
        search?: string;
        offset_start?: number;
        offset_end?: number;
    };
    [GetRoutes.PAGINATE_EMAILS]: {
        accounts: string;
        offset_start?: number;
        offset_end?: number;
    };
    [GetRoutes.GET_FOLDERS]: {
        accounts: string;
    };
    [GetRoutes.GET_EMAIL_CONTENT]: {
        accounts: string;
        folder: string;
        uid: string;
    };
}

interface PostBody {
    [PostRoutes.ADD_EMAIL_ACCOUNT]: {
        email: string
        password: string
        fullname: string
    };
    [PostRoutes.DELETE_EMAIL_ACCOUNT]: {
        account: string
    };
    [PostRoutes.DELETE_EMAIL_ACCOUNTS]: {};
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
    [PostRoutes.REFRESH_WHOLE_UNIVERSE]: {};
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
    ): Promise<Response> {
        const queryString = params
            ? "?" + new URLSearchParams(ApiService._removeUndefinedParams(params)).toString()
            : "";

        const response = await fetch(url + endpoint + queryString);
        return response.json();
    }

    static async post<T extends PostRoutes>(
        url: string,
        endpoint: T,
        body: PostBody[T] | FormData
    ): Promise<Response> {
        const response = await fetch(url + endpoint, {
            method: "POST",
            headers: body instanceof FormData
                ? {}
                : { "Content-Type": "application/json" },
            body: body instanceof FormData
                ? body
                : JSON.stringify(body),
        });
        return response.json();
    }
}
