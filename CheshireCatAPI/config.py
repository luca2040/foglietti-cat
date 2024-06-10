import json


class config_cat_API:

    on_message_called: bool = False

    def init(self, json_path: str) -> None:

        with open(json_path, "r") as file:
            data = json.load(file)

        ws_config = data["websocket"]

        self.base_url: str = ws_config["base_url"]
        self.port: int = int(ws_config["port"])
        self.user_id: str = ws_config["user_id"]
        self.auth_key: str = ws_config["auth_key"]
        self.secure_connection: bool = bool(ws_config["secure_connection"])

        rabbithole_config: str = data["rabbithole"]

        self.rabbit_url: str = rabbithole_config["url"]
        self.rabbit_finished_message: str = rabbithole_config["finished_message"]

        self.files_folder_path: str = data["folder"]
        self.log_file_path: str = data["log_file"]

    def message_called(self) -> None:
        self.on_message_called = True

    def get_message_state(self) -> bool:
        return self.on_message_called

    def reset_message_called(self) -> None:
        self.on_message_called = False


config = config_cat_API()
