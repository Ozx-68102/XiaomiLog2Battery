import os
import shutil
import time
import zipfile

from concurrent.futures import ProcessPoolExecutor
from flask import current_app, Response, jsonify
from typing import Literal
from werkzeug.datastructures import FileStorage

from Modules import FolderOperator


class BatteryLoggingExtractor:
    def __init__(self) -> None:
        self.app_path = current_app.instance_path

        self.Fop = FolderOperator()
        self.tep = os.path.join(self.app_path, "temp")

    def __manage_temp_dir(self, option: Literal["del", "crt", "reset"], path: str | None = None) -> None:
        if not isinstance(path, str) or path is None:
            raise TypeError(f"'path' must be a string or None, not '{type(path).__name__}'.")

        if path.isspace():
            raise ValueError("It seems that you didn't specify a valid path. ")

        if path is None:
            temp_path = self.tep
        else:
            temp_path = os.path.join(self.tep, path)

        match option:
            case "del":
                self.Fop.delete_dir(temp_path)
            case "crt":
                self.Fop.create_dir(temp_path)
            case "reset":
                self.Fop.delete_dir(temp_path)
                self.Fop.create_dir(temp_path)
            case _:
                raise ValueError(f"Variable 'option' must be one of 'del', 'crt' or 'reset', not '{option}'(type: {type(option).__name__}).'")

    def _multi_decompress_func(self, filepath: str) -> list[str] | tuple[Response, int] | None:
        try:
            step = 1
            if not filepath.startswith("bugreport") and not filepath.endswith(".zip"):
                error_text = {
                    "msg": f"Failed to decompress file in path: {filepath}",
                    "ErrorType": "Unsupported Media Type",
                    "reason": f"File named '{os.path.basename(filepath)}' in path '{filepath}' is not a valid zip file."
                }
                return jsonify(error_text), 415

            name = os.path.basename(filepath).split(sep=".", maxsplit=1)[0]
            temp_path = os.path.join(self.tep, f"temp_{name}")
            self.__manage_temp_dir(option="del", path=temp_path)

            current_file = filepath

            while current_file:
                try:
                    self.__manage_temp_dir(option="crt", path=temp_path)
                    with zipfile.ZipFile(file=current_file, mode="r") as zip_ref:
                        zip_ref.extractall(path=temp_path)
                        file_list = zip_ref.namelist()

                except zipfile.BadZipFile as e:
                    error_text = {
                        "msg": f"Failed to decompress file in path: {filepath}",
                        "ErrorType": "Bad Zip File",
                        "reason": str(e)
                    }
                    return jsonify(error_text), 400

                nested_zip = None
                for file in file_list:
                    if file.startswith("bugreport") and file.endswith(".zip"):
                        nested_zip = os.path.join(temp_path, file)
                        break

                if nested_zip:
                    current_file = nested_zip
                    step += 1
                else:
                    current_file = None

        # TODO: not complete

        except (ValueError, Exception) as e:
            error_text = {
                "msg": f"Failed to decompress file in path: {filepath}",
                "ErrorType": "Internal Server Error",
                "reason": str(e)
            }
            return jsonify(error_text), 500



    def decompress_xiaomi_log(self, files: list[str]):
        if len(files) == 0:
            error_text = {
                "msg": f"Failed to compress file.",
                "ErrorType": "Empty File List",
                "reason": "No files uploaded."
            }
            return jsonify(error_text), 400

        self.__manage_temp_dir(option="reset", path=self.tep)
        processed_files = []
        total_files = len(files)

        # TODO: Try to be decided by users
        workers = min(total_files, os.cpu_count(), 8)

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self._multi_decompress_func, file) for file in files]

        # TODO: not complete
