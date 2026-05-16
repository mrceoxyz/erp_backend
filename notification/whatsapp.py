import requests
from django.conf import settings


def send_whatsapp_message(phone, message):
    payload = {
        "to": phone,
        "type": "text",
        "text": {"body": message},
    }

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    requests.post(
        settings.WHATSAPP_API_URL,
        json=payload,
        headers=headers,
        timeout=10
    )
