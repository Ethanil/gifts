from flask import send_from_directory, abort, current_app
from os import getenv
from pathlib import Path
import mimetypes

def serve_image(image_name: str):
    storage = getenv("PICTURE_STORAGE")
    if not storage:
        abort(500, "PICTURE_STORAGE not configured")

    storage_path = Path(storage)
    if not storage_path.exists() or not storage_path.is_dir():
        abort(404, "Image storage folder not found")

    if Path(image_name).name != image_name:
        abort(400, "Invalid image name")

    file_path = storage_path / image_name
    if not file_path.exists() or not file_path.is_file():
        abort(404, f"Image {image_name} not found")

    mimetype, _ = mimetypes.guess_type(str(file_path))
    return send_from_directory(directory=str(storage_path), path=image_name, mimetype=mimetype)