import os
import shutil

from flask import Response, jsonify

class FolderOperator:
    @staticmethod
    def __empty_path(path: str) -> None:
        if not isinstance(path, str):
            raise TypeError(f"Variable 'path' must be a string, not '{type(path).__name__}'.")

        if path.isspace():
            raise ValueError("It seems that you didn't specify a valid path. ")

    def create_dir(self, path: str) -> tuple[Response, int]:
        try:
            self.__empty_path(path=path)
            os.makedirs(name=path, exist_ok=True)
            return jsonify({"msg": f"Successfully create directory in path: {path}."}), 200
        except OSError as e:
            return jsonify({"msg": f"Failed to create directory in path: {path}. Reason: {e.strerror}"}), 500
        except (TypeError, ValueError, Exception) as e:
            return jsonify({"msg": f"Failed to create directory in path: {path}. Reason: {str(e)}"}), 500

    def delete_dir(self, path: str) -> tuple[Response, int]:
        try:
            self.__empty_path(path=path)
        except (TypeError, ValueError) as e:
            return jsonify({"msg": f"Failed to delete directory in path: {path}. Reason: {str(e)}"}), 500

        if not os.path.exists(path=path):
            return jsonify({"msg": f"Failed to delete directory in path: {path} because directory does not exist."}), 404
        else:
            try:
                shutil.rmtree(path=path)
                return jsonify({"msg": f"Successfully deleted directory in path: {path}."}), 200
            except (FileNotFoundError, PermissionError, shutil.Error) as e:
                return jsonify({"msg": f"Failed to delete directory in path: {path}. Reason: {e.strerror}"}), 500
            except Exception as e:
                return jsonify({"msg": f"Failed to delete directory in path: {path}. Reason: {str(e)}"}), 500


if __name__ == "__main__":
    pass
