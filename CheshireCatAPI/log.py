from config import config
from datetime import datetime


def log(data: str, type: str) -> None:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    with open(config.log_file_path, "a") as logfile:
        logfile.write(f"{dt_string} - {type} - {data}\n")


def delete_log():
    with open(config.log_file_path, "w") as f:
        f.write("")
