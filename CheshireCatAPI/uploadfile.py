import requests


def upload_file(
    filepath,
    filename,
    stream=None,
    user="user",
    type="text/plain",
    url="http://localhost:1865/rabbithole/",
):

    files = {"file": (filename, stream or open(filepath, "rb"), type)}
    data = {"chunk_size": "", "chunk_overlap": ""}

    headers = {"accept": "application/json", "user_id": user}

    response = requests.post(url, headers=headers, files=files, data=data)

    return response
