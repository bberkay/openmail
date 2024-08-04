import json, logging, sys, socket, os
from urllib.parse import unquote
from typing import Optional, List, Callable
from logging.handlers import RotatingFileHandler

import uvicorn, sqlcipher3
from pydantic import BaseModel
from openmail import OpenMail, SearchCriteria
from openmail.utils import make_size_human_readable
from fastapi import FastAPI, File, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet

from consts import *

logger = None

def setup_logger():
    global logger
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(UVICORN_LOG_FILE_PATH, maxBytes=1*1024*1024, backupCount=5)
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

openmail = OpenMail()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
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

def as_response(response: tuple, success_callback: Optional[Callable] = None, failure_callback: Optional[Callable] = None) -> Response:
    if response[0] and success_callback:
        success_callback()
    elif failure_callback:
        failure_callback()

    if len(response) > 2:
        return Response(success=response[0], message=response[1], data=response[2])
    else:
        return Response(success=response[0], message=response[1])

"""
Temporary solution to get the email and password from the accounts.json file.
"""
accounts = json.load(open("./accounts.json"))
EMAIL = accounts[0]["email"]
PASSWORD = accounts[0]["password"]

def register_email(email: str, password: str):
    cipher_key = get_cipher_key()
    conn, cursor = get_db_conn()
    cursor.execute(
        "INSERT INTO credentials (email, password) VALUES (?, ?)",
        (email, Fernet(cipher_key).encrypt(password.encode()).decode())
    )
    conn.commit()
    conn.close()

@app.get("/get-accounts")
def get_accounts():
    try:
        chiper_key = get_cipher_key()
        chiper_suite = Fernet(chiper_key)
        conn, cursor = get_db_conn()
        cursor.execute("SELECT email, password FROM credentials")
        accounts = cursor.fetchall()
        conn.close()
        if accounts:
            accounts = [
                {
                    "email": account[0],
                    "password": chiper_suite.decrypt(account[1]).decode()
                }
                for account in accounts
            ]
        return Response(success=True, message="No accounts found")
    except Exception as e:
        return Response(success=False, message=str(e))

@app.post("/register")
def register(
    fullname = Form(...),
    email = Form(...),
    password = Form(...)
) -> Response:
    return as_response(openmail.connect(EMAIL, PASSWORD), register_email(EMAIL, PASSWORD))

@app.post("/login")
def login():
    pass

@app.get("/get-emails")
def get_emails(
    folder: str = 'INBOX',
    search: str = 'ALL',
    offset: str = '0'
) -> Response:
    return as_response(openmail.get_emails(
        unquote(folder),
        unquote(search),
        int(offset)
    ))

@app.get("/get-email-content/{folder}/{uid}")
def get_email_content(
    folder: str,
    uid: str
) -> Response:
    return as_response(openmail.get_email_content(uid, unquote(folder)))

@app.post("/send-email")
async def send_email(
    sender_name: str = Form(...), # TODO: This is going to change to sender: Tuple[str, str]
    receivers: str = Form(...), # mail addresses separated by comma
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(None)
) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).send_email(
        (sender_name, EMAIL) if sender_name else EMAIL,
        receivers,
        subject,
        body,
        attachments
    ))

@app.get("/get-folders")
def get_folders() -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).get_folders())

class SearchRequest(BaseModel):
    folder: str
    search: SearchCriteria
    offset: int

@app.post("/search-emails")
def search_emails(search_request: SearchRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).get_emails(
        search_request.folder,
        search_request.search,
        search_request.offset
    ))

class MarkEmailRequest(BaseModel):
    uid: str
    mark: str
    folder: str = 'INBOX'

@app.post("/mark-email")
async def mark_email(mark_email_request: MarkEmailRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).mark_email(
        mark_email_request.uid,
        mark_email_request.mark,
        mark_email_request.folder
    ))

class MarkEmailRequest(BaseModel):
    uid: str
    source: str
    destination: str

@app.post("/move-email")
async def move_email(move_email_request: MarkEmailRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).move_email(
        move_email_request.uid,
        move_email_request.source,
        move_email_request.destination
    ))

class DeleteEmailRequest(BaseModel):
    uid: str
    folder: str = 'INBOX'

@app.post("/delete-email")
async def delete_email(delete_email_request: DeleteEmailRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).delete_email(
        delete_email_request.uid,
        delete_email_request.folder
    ))

class CreateFolderRequest(BaseModel):
    folder_name: str
    parent_folder: str | None = None

@app.post("/create-folder")
async def create_folder(create_folder_request: CreateFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).create_folder(
        create_folder_request.folder_name,
        create_folder_request.parent_folder
    ))

class RenameFolderRequest(BaseModel):
    folder_name: str
    new_name: str

@app.post("/rename-folder")
async def rename_folder(rename_folder_request: RenameFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).rename_folder(
        rename_folder_request.folder_name,
        rename_folder_request.new_name
    ))

class DeleteFolderRequest(BaseModel):
    folder_name: str

@app.post("/delete-folder")
async def delete_folder(delete_folder_request: DeleteFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).delete_folder(delete_folder_request.folder_name))

class MoveFolderRequest(BaseModel):
    folder_name: str
    destination_folder: str

@app.post("/move-folder")
async def move_folder(move_folder_request: MoveFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).move_folder(
        move_folder_request.folder_name,
        move_folder_request.destination_folder
    ))

def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_free_port(start_port, end_port):
    if is_port_available(start_port):
        return port

    for port in range(start_port + 1, end_port + 1):
        if is_port_available(port):
            return port
    raise RuntimeError("No free ports available in the specified range")

if __name__ == "__main__":
    create_dirs_if_not_exists()
    setup_logger()
    create_keys_if_not_exits()
    create_tables_if_not_exists()
    host = "127.0.0.1"
    port = find_free_port(8000, 9000)
    pid = str(os.getpid())
    with open(UVICORN_PID_FILE_PATH, "w") as pid_file:
        pid_file.write(pid)
    with open(UVICORN_URL_FILE_PATH, "w") as server_file:
        server_file.write(f"http://{host}:{str(port)}")
    logger.info("Starting server at http://%s:%d | PID: %s", host, port, pid)
    uvicorn.run(
        app,
        host=host,
        port=port
    )
