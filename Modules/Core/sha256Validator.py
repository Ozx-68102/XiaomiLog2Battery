import hashlib
import os

from werkzeug.datastructures import FileStorage

def _get_file_storage_size(file: FileStorage) -> int:
    file.stream.seek(0, 2)
    file_size = file.stream.tell()
    file.stream.seek(0)

    return file_size


class SHA256Validator:
    def __init__(self, chunk_size: int = 2 ** 20):  # default chunk == 2 ** 20 => 2^20
        self.chunk_size = chunk_size

    @staticmethod
    def generate_string_hash(text: str) -> str:
        """generate sha256 of string"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def generate_file_hash(self, file_path: str) -> str:
        """generate sha256 of file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        if not os.path.isfile(file_path):
            raise ValueError(f"It is not a file: {file_path}")
        if os.path.getsize(file_path) == 0:
            raise ValueError(f"Sha256 can't be generate because its size is 0: {file_path}")

        sha256_hash = hashlib.sha256()
        if os.path.getsize(file_path) > 500 * 1024 ** 2: # suitable for huge file
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b""):
                    sha256_hash.update(chunk)
        else:   # for small file
            with open(file_path, "rb") as f:
                sha256_hash.update(f.read())
        return sha256_hash.hexdigest()

    def generate_file_storage_hash(self, file: FileStorage) -> str:
        """generate sha256 of FileStorage object"""
        if _get_file_storage_size(file=file) == 0:
            raise ValueError(f"Sha256 can't be generated because the FileStorage object is empty. File name: {file.filename}")

        sha256_hash = hashlib.sha256()
        file.stream.seek(0)
        if file.content_length > 500 * 1024 ** 2:
            while True:
                chunk = file.stream.read(self.chunk_size)
                if not chunk:
                    break
                sha256_hash.update(chunk)
        else:
            sha256_hash.update(file.stream.read())
        file.stream.seek(0)
        return sha256_hash.hexdigest()

    def validate_file_hash(self, file_path: str | FileStorage, expected_hash: str) -> bool:
        """validate sha256 of file"""
        try:
            if isinstance(file_path, str):
                actual_hash = self.generate_file_hash(file_path=file_path)
            elif isinstance(file_path, FileStorage):
                actual_hash = self.generate_file_storage_hash(file=file_path)
            else:
                raise TypeError(f"Unsupported file type: '{type(file_path).__name__}'.")

            return actual_hash.lower() == expected_hash.lower()
        except (ValueError, TypeError, FileNotFoundError) as e:
            print(f"Validating failed: {str(e)}.")
            return False


if __name__ == "__main__":
    pass
