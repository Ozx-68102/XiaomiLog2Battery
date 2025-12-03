import os
import shutil
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor, Future

from Modules.FileProcess.FolderOperator import FolderOperator, INSTANCE_PATH


def decompress(source: str, target: str) -> list[str]:
    """
    Decompress a zip file.
    :param source: Source path (include filename) .
    :param target: Target path.
    :raise zipfile.BadZipFile: If zip file cannot be decompressed.
    :return: A list of filenames in the decompressed zip file.
    """

    with zipfile.ZipFile(file=source, mode="r") as zip_ref:
        zip_ref.extractall(path=target)
        return zip_ref.namelist()


class BatteryLogProcessor:
    def __init__(self) -> None:
        self.top_temp = os.path.join(INSTANCE_PATH, "temp")
        self.final_path = os.path.join(INSTANCE_PATH, "extracted_txt")

        self.fop = FolderOperator()
        self.fop.create_dir(path=self.top_temp)
        self.fop.create_dir(path=self.final_path)

    def _extract_single_log(self, fp: str) -> str | None:
        """
        Extract a Xiaomi log file from a specified Xiaomi zip file.
        :param fp: Filepath.
        :return: A string containing the Xiaomi log filepath.
        """
        if not os.path.isfile(fp) or not os.path.isdir(os.path.dirname(fp)):
            raise ValueError(f"Variable '{fp}' is not a valid file path.")

        filename = os.path.basename(fp)
        if not filename.startswith("bugreport") or not filename.endswith(".zip"):
            raise ValueError(f"'{filename}' not a valid Xiaomi zip filepath.")

        # All operations here based on temp file.
        with tempfile.TemporaryDirectory(dir=self.top_temp, prefix="temp-") as temp_dir:
            try:
                # First we need to decompress nested zip file
                current_path = fp
                while True:
                    decompressed_files = decompress(source=current_path, target=temp_dir)

                    nested_zip = None
                    for decompressed_file in decompressed_files:
                        de_filename = os.path.basename(decompressed_file)
                        if de_filename.startswith("bugreport") and de_filename.endswith(".zip"):
                            nested_zip = os.path.join(temp_dir, decompressed_file)
                            break

                    if not nested_zip:  # Exit loop
                        break

                    current_path = nested_zip

                # Next we need to find out the specified txt file and move it
                target_filepath = None
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.startswith("bugreport") and file.endswith(".txt"):
                            target_filepath = os.path.join(root, file)
                            break

                    if target_filepath:
                        break

                if not target_filepath:
                    raise ValueError("Decompression successfully but no valid file found.")

                shutil.copy2(src=target_filepath, dst=self.final_path)
                return os.path.join(self.final_path, os.path.basename(target_filepath))
            except Exception as e:
                raise RuntimeError(f"Failed to process {os.path.basename(fp)}: {e}")

    def process_xiaomi_log(self, fps: list[str], thread_count: int) -> list[str]:
        """
        Process or extract one or more Xiaomi log files from zip files.
        :param fps: A list of Xiaomi zip file paths.
        :param thread_count: Number of worker threads/processes.
        :return: A list of extracted Xiaomi log files.
        """
        if not isinstance(fps, list):
            raise TypeError(f"Variable 'fps' must be a list, not '{type(fps).__name__}'.")

        if not fps:
            return []

        if thread_count < 1:
            raise ValueError(f"Thread count must be greater than 0, current value: {thread_count}")

        final_paths = []
        # Use the provided thread count directly
        workers = min(len(fps), thread_count)

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures: list[Future] = [executor.submit(self._extract_single_log, file) for file in fps]

            for future in futures:
                try:
                    results = future.result()
                    if results:
                        final_paths.append(results)
                except Exception as e:
                    print(e)
                    continue

        self.fop.reset_dir(path=self.top_temp)
        return final_paths


if __name__ == "__main__":
    pass
