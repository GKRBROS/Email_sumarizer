import time
import os
import base64

from config import load_config
from gmail_client import GmailClient, parse_message
from notifiers import (
    TelegramNotifier,
    WatiNotifier,
    build_customer_wati_message,
    build_telegram_message,
)
from state_store import StateStore
from summarizer import RouterSummarizer


def _materialize_gmail_files_from_env(credentials_file: str, token_file: str) -> None:
    credentials_b64 = os.getenv("GMAIL_CREDENTIALS_JSON_B64", "").strip()
    token_b64 = os.getenv("GMAIL_TOKEN_JSON_B64", "").strip()

    if credentials_b64:
        decoded = base64.b64decode(credentials_b64).decode("utf-8")
        with open(credentials_file, "w", encoding="utf-8") as file:
            file.write(decoded)

    if token_b64:
        decoded = base64.b64decode(token_b64).decode("utf-8")
        with open(token_file, "w", encoding="utf-8") as file:
            file.write(decoded)



def run() -> None:
    config = load_config()

    _materialize_gmail_files_from_env(
        credentials_file=config.gmail_credentials_file,
        token_file=config.gmail_token_file,
    )

    if not config.router_api_key:
        raise RuntimeError("ROUTER_API_KEY is required")
    if not config.telegram_bot_token or not config.telegram_admin_group_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_GROUP_ID (or TELEGRAM_CHAT_ID) are required")

    gmail = GmailClient(
        credentials_file=config.gmail_credentials_file,
        token_file=config.gmail_token_file,
        user_id=config.gmail_user_id,
    )
    store = StateStore(config.state_file)
    summarizer = RouterSummarizer(
        api_url=config.router_api_url,
        api_key=config.router_api_key,
        model=config.router_model,
        timeout_seconds=config.router_timeout_seconds,
    )

    telegram = TelegramNotifier(
        bot_token=config.telegram_bot_token,
        chat_id=config.telegram_admin_group_id,
        parse_mode=config.telegram_parse_mode,
    )

    wati = WatiNotifier(
        base_url=config.wati_base_url,
        api_token=config.wati_api_token,
        to=config.wati_to,
        send_message_path_template=config.wati_send_message_path_template,
    )

    while True:
        try:
            message_ids = gmail.list_new_message_ids(limit=10)
            message_ids.reverse()

            for message_id in message_ids:
                if store.has(message_id):
                    continue

                raw_message = gmail.get_message(message_id)
                email = parse_message(raw_message)
                summary = summarizer.summarize_email(email)

                telegram_message = build_telegram_message(config.telegram_template, email, summary)
                telegram.send(telegram_message)

                if config.wati_enabled:
                    wati_message = (
                        f"New email from {email['from_name']} <{email['from_email']}>\\n"
                        f"Subject: {email['subject']}\\n"
                        f"Summary: {summary['summary']}\\n"
                        f"Key Points: {summary['key_points']}"
                    )
                    wati.send(wati_message)

                if config.customer_wati_autoreply_enabled and email.get("customer_phone"):
                    if config.customer_wati_use_template_api:
                        wati.send_template(
                            to=email["customer_phone"],
                            path_template=config.wati_template_message_path_template,
                            template_name=config.customer_wati_template_name,
                            language=config.customer_wati_template_language,
                            connected_phone_number=config.wati_connected_phone_number,
                        )
                    else:
                        customer_message = build_customer_wati_message(
                            config.customer_wati_template,
                            email,
                        )
                        wati.send_to(email["customer_phone"], customer_message)

                if config.mark_as_read_after_process:
                    gmail.mark_as_read(message_id)

                store.add(message_id)

        except Exception as error:
            print(f"[ERROR] {error}")

        time.sleep(config.gmail_poll_interval_seconds)


if __name__ == "__main__":
    run()
