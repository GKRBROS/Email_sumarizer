import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppConfig:
    gmail_credentials_file: str
    gmail_token_file: str
    gmail_poll_interval_seconds: int
    gmail_user_id: str
    mark_as_read_after_process: bool
    router_api_url: str
    router_api_key: str
    router_model: str
    router_timeout_seconds: int
    telegram_bot_token: str
    telegram_chat_id: str
    telegram_admin_group_id: str
    telegram_parse_mode: str
    telegram_summary_only: bool
    telegram_template: str
    wati_enabled: bool
    wati_base_url: str
    wati_api_token: str
    wati_to: str
    wati_send_message_path_template: str
    wati_template_message_path_template: str
    wati_connected_phone_number: str
    customer_wati_autoreply_enabled: bool
    customer_wati_use_template_api: bool
    customer_wati_template_name: str
    customer_wati_template_language: str
    customer_wati_template: str
    state_file: str



def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}



def load_config() -> AppConfig:
    return AppConfig(
        gmail_credentials_file=os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json"),
        gmail_token_file=os.getenv("GMAIL_TOKEN_FILE", "token.json"),
        gmail_poll_interval_seconds=int(os.getenv("GMAIL_POLL_INTERVAL_SECONDS", "30")),
        gmail_user_id=os.getenv("GMAIL_USER_ID", "me"),
        mark_as_read_after_process=_get_bool("MARK_AS_READ_AFTER_PROCESS", False),
        router_api_url=os.getenv("ROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"),
        router_api_key=os.getenv("ROUTER_API_KEY", ""),
        router_model=os.getenv("ROUTER_MODEL", "qwen/qwen3-max"),
        router_timeout_seconds=int(os.getenv("ROUTER_TIMEOUT_SECONDS", "30")),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        telegram_admin_group_id=os.getenv("TELEGRAM_ADMIN_GROUP_ID", os.getenv("TELEGRAM_CHAT_ID", "")),
        telegram_parse_mode=os.getenv("TELEGRAM_PARSE_MODE", "HTML"),
        telegram_summary_only=_get_bool("TELEGRAM_SUMMARY_ONLY", True),
        telegram_template=os.getenv(
            "TELEGRAM_TEMPLATE",
            "<b>📩 New Contact (Admin Alert)</b>\\n"
            "<b>From:</b> {from_name} &lt;{from_email}&gt;\\n"
            "<b>Phone:</b> {customer_phone}\\n"
            "<b>Subject:</b> {subject}\\n"
            "<b>Summary:</b> {summary}\\n"
            "<b>Key Points:</b> {key_points}\\n"
            "<a href=\"{gmail_link}\">Open in Gmail</a>",
        ),
        wati_enabled=_get_bool("WATI_ENABLED", False),
        wati_base_url=os.getenv("WATI_BASE_URL", ""),
        wati_api_token=os.getenv("WATI_API_TOKEN", ""),
        wati_to=os.getenv("WATI_TO", ""),
        wati_send_message_path_template=os.getenv(
            "WATI_SEND_MESSAGE_PATH_TEMPLATE",
            "/api/v1/sendSessionMessage/{phone}",
        ),
        wati_template_message_path_template=os.getenv(
            "WATI_TEMPLATE_MESSAGE_PATH_TEMPLATE",
            "/api/v3/sendTemplateMessage/{phone}",
        ),
        wati_connected_phone_number=os.getenv("WATI_CONNECTED_PHONE_NUMBER", "919745004162"),
        customer_wati_autoreply_enabled=_get_bool("CUSTOMER_WATI_AUTOREPLY_ENABLED", False),
        customer_wati_use_template_api=_get_bool("CUSTOMER_WATI_USE_TEMPLATE_API", True),
        customer_wati_template_name=os.getenv("CUSTOMER_WATI_TEMPLATE_NAME", "email_customer"),
        customer_wati_template_language=os.getenv("CUSTOMER_WATI_TEMPLATE_LANGUAGE", "en"),
        customer_wati_template=os.getenv(
            "CUSTOMER_WATI_TEMPLATE",
            "Thank you for contacting Frame Forge. We will get back to you shortly.",
        ),
        state_file=os.getenv("STATE_FILE", "processed_state.json"),
    )
