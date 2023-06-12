import os


def handle_uploaded_file(file) -> str:
    path = "media/uploads/"
    if not os.path.exists(path):
        os.makedirs(path)

    path += f"{file}"

    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return f"{path}"
