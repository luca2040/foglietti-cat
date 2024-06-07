def on_open():
    print("Connection opened!")


def on_error(exception: Exception):
    print(str(exception))


def on_close(status_code: int, message: str):
    print(f"Connection closed with code {status_code}: {message}")
