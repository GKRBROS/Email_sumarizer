# Email Summarizer (No UI)

Backend service that:

- Checks Gmail for new emails
- Summarizes each email using your Router API
- Sends admin alerts to a Telegram group
- Optionally sends summary through WATI API
- Detects phone numbers in email and auto-replies customer through WATI API

## 1) Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill your values.
4. Put your Gmail OAuth `credentials.json` in the project root.
5. Use `ROUTER_MODEL=qwen/qwen3-max` and set `ROUTER_API_KEY` from your router provider dashboard.

## 2) Gmail API prerequisites

- Enable Gmail API in Google Cloud Console.
- Configure OAuth consent screen.
- Create OAuth Client credentials (Desktop app), download as `credentials.json`.
- First run will open browser login and create `token.json` automatically.

## 3) Run

```bash
python src/main.py
```

## 4) Telegram template variables

Use these placeholders inside `TELEGRAM_TEMPLATE` (for admin group alerts):

- `{from_name}`
- `{from_email}`
- `{customer_phone}`
- `{customer_phone_numbers}`
- `{subject}`
- `{snippet}`
- `{summary}`
- `{key_points}`
- `{gmail_link}`

Example template:

```text
<b>📩 New Contact (Admin Alert)</b>
<b>From:</b> {from_name} &lt;{from_email}&gt;
<b>Phone:</b> {customer_phone}
<b>Subject:</b> {subject}
<b>Summary:</b> {summary}
<b>Key Points:</b> {key_points}
<a href="{gmail_link}">Open in Gmail</a>
```

Set your admin group id in `TELEGRAM_ADMIN_GROUP_ID` (usually starts with `-100...`).

## 5) WATI notes

This project uses WATI API with:

- `WATI_BASE_URL`
- `WATI_API_TOKEN`
- `WATI_TO`
- `WATI_SEND_MESSAGE_PATH_TEMPLATE`
- `WATI_TEMPLATE_MESSAGE_PATH_TEMPLATE`
- `WATI_CONNECTED_PHONE_NUMBER`

Set `WATI_ENABLED=true` to activate.

## 6) Customer WATI auto-reply template

When `CUSTOMER_WATI_AUTOREPLY_ENABLED=true`, the app scans each email for phone numbers and sends an automatic reply to the first valid number found.

Config:

- `CUSTOMER_WATI_AUTOREPLY_ENABLED`
- `CUSTOMER_WATI_USE_TEMPLATE_API`
- `CUSTOMER_WATI_TEMPLATE_NAME`
- `CUSTOMER_WATI_TEMPLATE_LANGUAGE`
- `CUSTOMER_WATI_TEMPLATE`

Requested template setup:

- `CUSTOMER_WATI_TEMPLATE_NAME=email_customer`
- `CUSTOMER_WATI_TEMPLATE_LANGUAGE=en`
- `WATI_CONNECTED_PHONE_NUMBER=919745004162`
- `WATI_TEMPLATE_MESSAGE_PATH_TEMPLATE=/api/v3/sendTemplateMessage/{phone}`

Template placeholders supported:

- `{customer_phone}`
- `{from_name}`
- `{from_email}`
- `{subject}`

Example:

```text
Thank you for contacting Frame Forge. We will get back to you shortly.
```
