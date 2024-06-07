import time
import cheshire_cat_api as ccat
import os
import json

from websocket_functions import *
from uploadfile import upload_file


config = ccat.Config(
    base_url="localhost",
    port=1865,
    user_id="upload_websocket",
    auth_key="",
    secure_connection=False,
)
folder_path = "files/"

file_finished = False


def on_message(message: str):
    json_message = json.loads(message)

    if json_message["type"] == "notification":
        content_message: str = json_message["content"]

        print(content_message)

        if content_message.startswith("Finished reading "):
            global file_finished
            file_finished = True


cat_client = ccat.CatClient(
    config=config,
    on_open=on_open,
    on_close=on_close,
    on_message=on_message,
    on_error=on_error,
)

cat_client.connect_ws()

while not cat_client.is_ws_connected:
    time.sleep(1)

file_list = os.listdir(folder_path)
for file in file_list:
    file_path = os.path.join(folder_path, file)

    result = upload_file(file_path, file, user=config.user_id)
    print(result.json())

    while not file_finished:
        time.sleep(0.5)

    file_finished = False

cat_client.close()
