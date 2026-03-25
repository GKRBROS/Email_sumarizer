from typing import Dict

import requests


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str, parse_mode: str = "HTML"):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.parse_mode = parse_mode

    def send(self, text: str) -> None:
        if not self.bot_token or not self.chat_id:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": self.parse_mode,
            "disable_web_page_preview": False,
        }
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()


class WatiNotifier:
    def __init__(self, base_url: str, api_token: str, to: str, send_message_path_template: str):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.to = to
        self.send_message_path_template = send_message_path_template

    def _auth_header_value(self) -> str:
        token = (self.api_token or "").strip()
        if token.lower().startswith("bearer "):
            return token
        return f"Bearer {token}"

    def send(self, text: str) -> None:
        if not self.api_token or not self.base_url or not self.to:
            return

        self.send_to(self.to, text)

    def send_to(self, to: str, text: str) -> None:
        if not self.api_token or not self.base_url or not to:
            return

        path = self.send_message_path_template.format(phone=to)
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": self._auth_header_value(),
            "Content-Type": "application/json",
        }
        payload = {
            "messageText": text[:1024],
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

    def send_template(
        self,
        to: str,
        path_template: str,
        template_name: str,
        language: str,
        connected_phone_number: str,
    ) -> None:
        if not self.api_token or not self.base_url or not to:
            return

        path = path_template.format(phone=to)
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": self._auth_header_value(),
            "Content-Type": "application/json",
        }
        payload = {
            "template_name": template_name,
            "language": {"code": language},
            "broadcast_name": template_name,
            "parameters": [],
        }
        if connected_phone_number:
            payload["fromNumber"] = connected_phone_number

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()



def build_telegram_message(
    template: str,
    email: Dict[str, str],
    summary: Dict[str, str],
    summary_only: bool = False,
) -> str:
    gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{email['id']}"

    normalized_template = (
        (template or "")
        .replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .strip()
    )

    safe_values = {
        "from_name": email.get("from_name", "Unknown"),
        "from_email": email.get("from_email", "unknown@example.com"),
        "customer_phone": email.get("customer_phone", "Not found"),
        "customer_phone_numbers": email.get("customer_phone_numbers", "Not found"),
        "subject": email.get("subject", "(No Subject)"),
        "snippet": email.get("snippet", ""),
        "summary": summary.get("summary", "No summary."),
        "key_points": summary.get("key_points", "No key points."),
        "gmail_link": gmail_link,
    }

    if summary_only:
        return (
            "<b>📩 New Email Summary</b>\n"
            f"<b>Subject:</b> {safe_values['subject']}\n"
            f"<b>Summary:</b> {safe_values['summary']}\n"
            f"<b>Key Points:</b> {safe_values['key_points']}\n"
            f"<a href=\"{safe_values['gmail_link']}\">Open in Gmail</a>"
        )

    try:
        return normalized_template.format(**safe_values)
    except KeyError:
        fallback = (
            "<b>📩 New Contact (Admin Alert)</b>\n"
            f"<b>From:</b> {safe_values['from_name']} &lt;{safe_values['from_email']}&gt;\n"
            f"<b>Phone:</b> {safe_values['customer_phone']}\n"
            f"<b>Subject:</b> {safe_values['subject']}\n"
            f"<b>Summary:</b> {safe_values['summary']}\n"
            f"<b>Key Points:</b> {safe_values['key_points']}\n"
            f"<a href=\"{safe_values['gmail_link']}\">Open in Gmail</a>"
        )
        return fallback


def build_customer_wati_message(template: str, email: Dict[str, str]) -> str:
    safe_values = {
        "customer_phone": email.get("customer_phone", ""),
        "from_name": email.get("from_name", "Customer"),
        "from_email": email.get("from_email", ""),
        "subject": email.get("subject", ""),
    }
    try:
        return template.format(**safe_values)
    except KeyError:
        return template
