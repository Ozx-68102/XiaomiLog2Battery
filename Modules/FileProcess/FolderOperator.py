import os
import shutil

INSTANCE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "instance")

class FolderOperator:
    @staticmethod
    def __empty_path(path: str) -> None:
        if not isinstance(path, str):
            raise TypeError(f"Variable 'path' must be a string, not '{type(path).__name__}'.")

        if path.isspace():
            raise ValueError("It seems that you didn't specify a valid path. ")

    def create_dir(self, path: str) -> None:
        """
        Create a new directory (if not exists).
        """
        self.__empty_path(path=path)
        os.makedirs(name=path, exist_ok=True)

    def delete_dir(self, path: str) -> None:
        """
        Delete a specified directory and all its contents.
        """
        self.__empty_path(path=path)

        if not os.path.exists(path=path):
            raise FileNotFoundError(f"The path '{path}' does not exist.")

        shutil.rmtree(path=path)

    def reset_dir(self, path: str) -> None:
        """
        Delete a specified directory (include all its contents) and recreate it.
        """
        self.delete_dir(path=path)
        self.create_dir(path=path)


if __name__ == "__main__":
    pass
