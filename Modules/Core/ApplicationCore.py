import os

from flask import current_app, jsonify, Response
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from Modules.Core.sha256Validator import SHA256Validator, _get_file_storage_size
from WebPanel.models import FileUploaded, DuplicateDataError

HASH_VALIDATE = SHA256Validator()


def initialize(files: list[FileStorage]) -> tuple[Response, int]:
    pass


def danger_text(msg: str) -> str:
    return f"<span class=\"text-danger\">{msg}</span>"


def success_text(msg: str) -> str:
    return f"<span class=\"text-success\">{msg}</span>"


def _save_file(file: FileStorage, specified_path: str) -> str:
    filepath = os.path.join(specified_path, file.filename)
    if os.path.exists(filepath):
        return "file has already existed"
    else:
        # it will automatically overwrite files with the same name by default, but I don't want it to do that.
        file.save(dst=filepath)
        return "successful"


def upload_zip_files(files: list[FileStorage]) -> tuple[Response, int]:
    save_path = os.path.join(current_app.instance_path, "uploads")
    os.makedirs(name=save_path, exist_ok=True)

    error_files = {}  # format: {"filename": "error reason"}
    success_files = []

    for file in files:
        if not file or len(file.filename) == 0:
            error_files[file.filename] = "empty file"
            continue

        try:
            file_hash = HASH_VALIDATE.generate_file_storage_hash(file=file)
            size = _get_file_storage_size(file)
            FileUploaded.create(filename=file.filename, sha256=file_hash, filesize=size)
        except ValueError as e:
            error_files[file.filename] = f"sha256 generation error: {str(e)}"
        except DuplicateDataError:
            error_files[file.filename] = "duplicate file"  # TODO: Need to capture this issue and ask if overwrite
            continue
        except IntegrityError as e:
            error_files[file.filename] = f"Unknown error: {str(e)}"
            continue

        text = _save_file(file=file, specified_path=save_path)
        if text == "successful":
            success_files.append(file.filename)
        else:
            error_files[file.filename] = text

    response = {
        "msg": f"success: {len(success_files)}, failed: {len(error_files)}",
        "failed_files": error_files
    }
    if len(success_files) > 0:
        status_code = 200
    else:
        status_code = 400

    return jsonify(response), status_code
