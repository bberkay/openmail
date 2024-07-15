from openmail import OpenMail
from fastapi import FastAPI, Form
import json
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import Optional, List

class Response(BaseModel):
    success: bool
    message: Optional[str] = ''
    data: Optional[dict | list] = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
accounts = json.load(open("accounts.json"))

@app.post("/send-email")
def send_email(to: str = Form(...), subject: str = Form(...), body: str = Form(...)):
    email = accounts[0]["email"]
    password = accounts[0]["password"]
    success, message = OpenMail(email, password).send_email(to, subject, body)
    return {"success": success, "message": message}
