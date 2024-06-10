import json

from config import config
from log import log


def on_open():
    log("Connection opened", "INFO")


def on_error(exception: Exception):
    log(f"Error {str(exception)}", "ERROR")


def on_close(status_code: int, message: str):
    log(
        f"Connection closed with status code {status_code}: {message}",
        "INFO" if not status_code else "ERROR",
    )


def on_message(message: str) -> None:
    json_message = json.loads(message)

    if json_message["type"] == "notification":
        content_message: str = json_message["content"]

        log(content_message, "INFO")

        if content_message.startswith(config.rabbit_finished_message):
            config.message_called()
