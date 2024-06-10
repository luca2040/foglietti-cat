import time
import cheshire_cat_api as ccat
import os
import sys

from websocket_functions import *
from uploadfile import upload_file

from config import config
from log import log, delete_log

if __name__ == "__main__":
    config_filepath = sys.argv[1] if len(sys.argv) > 1 else "./config.json"
    config.init(config_filepath)

    delete_log()

    cat_client = ccat.CatClient(
        config=config,
        on_open=on_open,
        on_close=on_close,
        on_message=on_message,
        on_error=on_error,
    )

    cat_client.connect_ws()

    while not cat_client.is_ws_connected:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            log("KeyboardInterrupt", "ERROR")
            cat_client.close()

            try:
                sys.exit(1)
            except SystemExit:
                os._exit(1)

    file_list = os.listdir(config.files_folder_path)

    for file in file_list:
        file_path = os.path.join(config.files_folder_path, file)

        result = upload_file(file_path, file, config.rabbit_url, user=config.user_id)
        log(result.json(), "INFO")

        while not config.get_message_state():
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                log("KeyboardInterrupt", "ERROR")
                cat_client.close()

                try:
                    sys.exit(1)
                except SystemExit:
                    os._exit(1)

        config.reset_message_called()

    cat_client.close()
