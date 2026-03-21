import base64
import re
from email.utils import parseaddr
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailClient:
    def __init__(self, credentials_file: str, token_file: str, user_id: str):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.user_id = user_id
        self.service = self._build_service()

    def _build_service(self):
        creds = None
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        except Exception:
            creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w", encoding="utf-8") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def list_new_message_ids(self, limit: int = 10) -> List[str]:
        response = (
            self.service.users()
            .messages()
            .list(
                userId=self.user_id,
                q="in:inbox -category:social -category:promotions newer_than:1d",
                maxResults=limit,
            )
            .execute()
        )
        messages = response.get("messages", [])
        return [message["id"] for message in messages if "id" in message]

    def get_message(self, message_id: str) -> Dict:
        return (
            self.service.users()
            .messages()
            .get(userId=self.user_id, id=message_id, format="full")
            .execute()
        )

    def mark_as_read(self, message_id: str) -> None:
        self.service.users().messages().modify(
            userId=self.user_id,
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()



def _find_header(headers: List[Dict], name: str) -> str:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""



def _extract_text_from_payload(payload: Dict) -> str:
    if not payload:
        return ""

    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})
    data = body.get("data")

    if mime_type == "text/plain" and data:
        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return ""

    parts = payload.get("parts", [])
    for part in parts:
        content = _extract_text_from_payload(part)
        if content:
            return content

    if data:
        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return ""

    return ""


def _extract_phone_numbers(text: str) -> List[str]:
    if not text:
        return []

    pattern = re.compile(r"(?:\+?\d[\d\s\-().]{8,}\d)")
    matches = pattern.findall(text)

    numbers: List[str] = []
    seen = set()

    for item in matches:
        digits = re.sub(r"\D", "", item)
        if len(digits) < 10 or len(digits) > 15:
            continue
        if digits in seen:
            continue
        seen.add(digits)
        numbers.append(digits)

    return numbers



def parse_message(message: Dict) -> Dict[str, str]:
    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    raw_from = _find_header(headers, "From")
    from_name, from_email = parseaddr(raw_from)
    subject = _find_header(headers, "Subject")

    body_text = _extract_text_from_payload(payload)
    cleaned_body = re.sub(r"\s+", " ", body_text).strip()
    snippet = re.sub(r"\s+", " ", message.get("snippet", "")).strip()
    phone_numbers = _extract_phone_numbers(f"{subject}\n{snippet}\n{cleaned_body}")
    primary_phone = phone_numbers[0] if phone_numbers else ""

    return {
        "id": message.get("id", ""),
        "thread_id": message.get("threadId", ""),
        "from_name": from_name or "Unknown",
        "from_email": from_email or "unknown@example.com",
        "subject": subject or "(No Subject)",
        "snippet": snippet,
        "body": cleaned_body,
        "customer_phone": primary_phone,
        "customer_phone_numbers": ",".join(phone_numbers),
    }
