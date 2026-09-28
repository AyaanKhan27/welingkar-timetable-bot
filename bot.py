import os
import requests
import subprocess


TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
AUTHORIZED_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])

BASE_URL = (
    f"https://api.telegram.org/"
    f"bot{TELEGRAM_BOT_TOKEN}"
)


def telegram(method, data=None):

    response = requests.post(
        f"{BASE_URL}/{method}",
        data=data or {},
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def send_message(text):

    telegram(
        "sendMessage",
        {
            "chat_id": AUTHORIZED_CHAT_ID,
            "text": text
        }
    )


def get_updates():

    response = requests.get(
        f"{BASE_URL}/getUpdates",
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def main():

    print("Checking Telegram...")

    data = get_updates()

    if not data.get("ok"):

        print("Telegram API error.")
        return

    updates = data.get("result", [])

    print(
        f"Received {len(updates)} Telegram update(s)."
    )

    latest_update_id = None
    generate_requested = False

    for update in updates:

        latest_update_id = update["update_id"]

        message = update.get("message")

        if not message:
            continue

        chat = message.get("chat", {})

        chat_id = chat.get("id")

        # Only accept commands from you
        if chat_id != AUTHORIZED_CHAT_ID:
            print(
                "Ignoring message from "
                "unauthorized chat."
            )
            continue

        text = (
            message.get("text") or ""
        ).strip().lower()

        print(
            f"Received command: {text}"
        )

        if text == "/generate":

            generate_requested = True

    # Acknowledge received Telegram updates
    if latest_update_id is not None:

        telegram(
            "getUpdates",
            {
                "offset":
                    latest_update_id + 1
            }
        )

    if not generate_requested:

        print(
            "No /generate command found."
        )

        return

    print(
        "Generate command received!"
    )

    send_message(
        "🔄 Generating today's timetable...\n"
        "Logging into WeWorld."
    )

    # Run timetable extractor
    result = subprocess.run(
        ["python", "timetable.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(result.stdout)
        print(result.stderr)

        send_message(
            "❌ Timetable generation failed.\n\n"
            "Please try /generate again."
        )

        return

    output = result.stdout

    # Find the generated WhatsApp message
    marker = (
        "========== WHATSAPP MESSAGE =========="
    )

    if marker not in output:

        print(output)

        send_message(
            "❌ I logged into WeWorld, but "
            "couldn't generate the timetable "
            "message."
        )

        return

    message = output.split(
        marker,
        1
    )[1].strip()

    send_message(
        "✅ *Today's timetable is ready!*\n\n"
        + message
    )

    print(
        "Timetable sent to Telegram."
    )


if __name__ == "__main__":
    main()
