import os

UPLOAD_DIR = "uploads"

async def save_uploaded_file(file):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return file_path