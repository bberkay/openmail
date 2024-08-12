import json, logging, sys, socket, os, re, asyncio, concurrent.futures
from urllib.parse import unquote
from typing import Optional, List
from logging.handlers import RotatingFileHandler

import uvicorn, sqlcipher3
from pydantic import BaseModel
from openmail import OpenMail, SearchCriteria
from openmail.utils import make_size_human_readable
from fastapi import FastAPI, File, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet

from consts import *

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

def setup_logger():
    global logger
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(UVICORN_LOG_FILE_PATH, maxBytes=1*1024*1024, backupCount=5)
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

ACCOUNTS = json.loads(open("./accounts.json").read())
openmail_clients = {}
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hello")
async def hello():
    return Response(success=True, message="Hello, Server is ready for you!")

def create_dirs_if_not_exists():
    for directory in [APP_DIR, SECRETS_DIR, DB_DIR, LOG_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

def create_keys_if_not_exits():
    if not os.path.exists(PRAGMA_KEY_FILE_PATH):
        with open(PRAGMA_KEY_FILE_PATH, "wb") as key_file:
            key_file.write(Fernet.generate_key())

    if not os.path.exists(CIPHER_KEY_FILE_PATH):
        with open(CIPHER_KEY_FILE_PATH, "wb") as key_file:
            key_file.write(Fernet.generate_key())

def get_pragma_key() -> bytes:
    with open(PRAGMA_KEY_FILE_PATH, "rb") as key_file:
        return key_file.read()

def get_cipher_key() -> bytes:
    with open(CIPHER_KEY_FILE_PATH, "rb") as key_file:
        return key_file.read()

def get_db_conn():
    conn = sqlcipher3.connect(UVICORN_DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA key = '{get_pragma_key().decode()}'")
    cursor.execute("VACUUM")
    return conn, cursor

def create_tables_if_not_exists():
    conn, cursor = get_db_conn()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname VARCHAR(50),
            email VARCHAR(100) NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def summarize_data(response_data: any) -> any:
    if isinstance(response_data, dict):
        return {key: summarize_data(value) for key, value in response_data.items()}
    elif isinstance(response_data, list):
        return summarize_data(str(response_data))
    elif isinstance(response_data, str) and len(response_data) >= 100:
        return response_data[:100] + '...' + (']' if response_data.startswith('[') else '')
    return response_data

async def extract_response_body(response: FastAPIResponse) -> bytes:
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    return response_body

def extract_response_data(response_body: bytes) -> any:
    try:
        return json.loads(response_body)
    except Exception as e:
        return response_body.decode("utf-8")

async def save_request_response_log(request: Request, response: FastAPIResponse):
    try:
        response_data = extract_response_data(response._body)
        log_message = (
            f"{request.method} {request.url} - {response.status_code} - "
            f"{summarize_data(response_data)} - "
            f"{make_size_human_readable(int(response.headers.get('content-length')))}"
        )
        if response.status_code >= 400:
            logger.error(log_message)
        elif response.status_code != 307: # Temporary Redirect
            logger.info(log_message)
    except Exception as e:
        logger.error(f"Error while logging request and response: {e}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    response._body = await extract_response_body(response)
    await save_request_response_log(request, response)
    return FastAPIResponse(
        content=response._body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None

def is_email_valid(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))

def add_email_account_to_db(email: str, password: str, fullname: str = None) -> tuple[bool, str]:
    cipher_key = get_cipher_key()
    conn, cursor = get_db_conn()
    if not cursor.execute("SELECT email FROM accounts WHERE email = ?", (email,)).fetchone():
        cursor.execute(
            "INSERT INTO accounts (fullname, email, password) VALUES (?, ?, ?)",
            (fullname, email, Fernet(cipher_key).encrypt(password.encode()).decode())
        )
        conn.commit()
        conn.close()
        return True, "Email account added successfully"
    else:
        conn.close()
        return False, "Email account already exists"

@app.post("/add-email-account")
def add_email_account(
    email = Form(...),
    password = Form(...),
    fullname = Form(None)
) -> Response:
    if not is_email_valid(email):
        return Response(success=False, message="Invalid email address format")

    openmail_client = OpenMail()
    if not openmail_client.connect(email, password):
        return Response(success=False, message="Invalid email credentials")

    success, message = add_email_account_to_db(email, password, fullname)
    if success:
        openmail_clients[email] = openmail_client
        return Response(success=success, message=message, data={"email": email, "fullname": fullname})
    return Response(success=success, message=message)

def get_email_accounts_from_db(emails: List[str] | None = None, columns: List[str] = ["fullname", "email", "password"]) -> list[dict] | None:
    chiper_key = get_cipher_key()
    chiper_suite = Fernet(chiper_key)
    conn, cursor = get_db_conn()
    where_clause = f" WHERE email IN ({', '.join(['?' for _ in emails])})" if emails else ""
    cursor.execute(f"SELECT {', '.join(columns)} FROM accounts" + where_clause, emails or [])
    accounts = cursor.fetchall()
    conn.close()
    if accounts:
        return [
            {columns[i]: account[i] if columns[i] != "password" else chiper_suite.decrypt(account[i].encode()).decode() for i in range(len(columns))}
            for account in accounts
        ]
    else:
        return None

def create_openmail_clients_from_db():
    accounts = get_email_accounts_from_db(None, ["email", "password"])
    if not accounts:
        return

    for account in accounts:
        openmail_clients[account["email"]] = OpenMail()
        openmail_clients[account["email"]].connect(account["email"], account["password"])
        #openmail_clients[account["email"]].idle()

def reconnect_logged_out_openmail_clients():
    for email, openmail_client in openmail_clients.items():
        if not openmail_client.is_logged_in():
            openmail_client.connect(email, get_email_accounts_from_db([email], ["password"])[0]["password"])

@app.on_event("startup")
def startup_event():
    create_openmail_clients_from_db()

@app.get("/get-email-accounts")
def get_email_accounts() -> Response:
    try:
        return Response(
            success=True,
            message="Email accounts fetched successfully",
            data=get_email_accounts_from_db(None, ["fullname", "email"])
        )
    except Exception as e:
        return Response(success=False, message=str(e))

def run_openmail_func_concurrently(accounts: list, func, **params) -> List[dict]:
    result = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_emails = {
            executor.submit(func, client, **params): email for email, client in openmail_clients.items() if email in accounts
        }

        for future in concurrent.futures.as_completed(future_to_emails):
            email = future_to_emails[future]
            future = future.result()
            result.append({"email": email, "data": future})

    return result

@app.get("/get-emails/{accounts}")
async def get_emails(
    accounts: str,
    folder: Optional[str] = "INBOX",
    search: Optional[str] = "ALL",
    offset: Optional[int] = 0
) -> Response:
    try:
        return Response(
            success=True,
            message="Emails found",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client, **params: client.get_emails(**params),
                folder=folder,
                search=search,
                offset=offset
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.get("/get-folders/{accounts}")
async def get_folders(
    accounts: str,
) -> Response:
    try:
        return Response(
            success=True,
            message="Folders found",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client: client.get_folders(),
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.get("/get-email-content/{email}/{folder}/{uid}")
def get_email_content(
    email: str,
    folder: str,
    uid: str
) -> Response:
    try:
        if email not in openmail_clients:
            return Response(success=False, message="Email account not found")

        return Response(
            success=True,
            message="Email content fetched",
            data=openmail_clients[email].get_email_content(uid, unquote(folder))
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.post("/send-email")
async def send_email(
    sender: str | tuple[str, str] = Form(...), # (sender_name, sender_email)
    receivers: str = Form(...), # mail addresses separated by comma
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(None)
) -> Response:
    try:
        return Response(
            success=True,
            message="Email sent",
            data=openmail_clients[(sender if isinstance(sender, str) else sender[1])].send_email(
                sender,
                receivers,
                subject,
                body,
                attachments
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class MarkEmailRequest(BaseModel):
    email: str
    uid: str
    mark: str
    folder: str = 'INBOX'

@app.post("/mark-email")
async def mark_email(mark_email_request: MarkEmailRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Email marked successfully",
            data=openmail_clients[mark_email_request.email].mark_email(
                mark_email_request.uid,
                mark_email_request.mark,
                mark_email_request.folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class MoveEmailRequest(BaseModel):
    email: str
    uid: str
    source: str
    destination: str

@app.post("/move-email")
async def move_email(move_email_request: MoveEmailRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Email moved successfully",
            data=openmail_clients[move_email_request.email].move_email(
                move_email_request.uid,
                move_email_request.source,
                move_email_request.destination
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class DeleteEmailRequest(BaseModel):
    email: str
    uid: str
    folder: str = 'INBOX'

@app.post("/delete-email")
async def delete_email(delete_email_request: DeleteEmailRequest) -> Response:
    try:
        return Response(
            success=True,
            messages="Email deleted successfully",
            data=openmail_clients[delete_email_request.email].delete_email(
                delete_email_request.uid,
                delete_email_request.folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class CreateFolderRequest(BaseModel):
    email: str
    folder_name: str
    parent_folder: str | None = None

@app.post("/create-folder")
async def create_folder(create_folder_request: CreateFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder created successfully",
            data=openmail_clients[create_folder_request.email].create_folder(
                create_folder_request.folder_name,
                create_folder_request.parent_folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class RenameFolderRequest(BaseModel):
    email: str
    folder_name: str
    new_name: str

@app.post("/rename-folder")
async def rename_folder(rename_folder_request: RenameFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder renamed successfully",
            data=openmail_clients[rename_folder_request.email].rename_folder(
                rename_folder_request.folder_name,
                rename_folder_request.new_name
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class DeleteFolderRequest(BaseModel):
    folder_name: str

@app.post("/delete-folder")
async def delete_folder(delete_folder_request: DeleteFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder deleted successfully",
            data=openmail_clients[delete_folder_request.email].delete_folder(
                delete_folder_request.folder_name
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class MoveFolderRequest(BaseModel):
    email: str
    folder_name: str
    destination_folder: str

@app.post("/move-folder")
async def move_folder(move_folder_request: MoveFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder moved successfully",
            data=openmail_clients[move_folder_request.email].move_folder(
                move_folder_request.folder_name,
                move_folder_request.destination_folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_free_port(start_port, end_port):
    if is_port_available(start_port):
        return start_port

    for port in range(start_port + 1, end_port + 1):
        if is_port_available(port):
            return port
    raise RuntimeError("No free ports available in the specified range")

def write_uvicorn_info_file(host: str, port: str, pid: str):
    with open(UVICORN_INFO_FILE_PATH, "w") as info_file:
        info_file.write(f"URL=http://{host}:{port}\n")
        info_file.write(f"PID={pid}")

if __name__ == "__main__":
    create_dirs_if_not_exists()
    setup_logger()
    create_keys_if_not_exits()
    create_tables_if_not_exists()
    host = "127.0.0.1"
    port = find_free_port(8000, 9000)
    pid = str(os.getpid())
    write_uvicorn_info_file(host, str(port), pid)
    logger.info("Starting server at http://%s:%d | PID: %s", host, port, pid)
    uvicorn.run(
        app,
        host=host,
        port=port
    )
