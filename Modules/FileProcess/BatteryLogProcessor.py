import os
import shutil
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor, Future

from Modules.FileProcess.FolderOperator import FolderOperator, INSTANCE_PATH


def decompress(source: str, target: str, step: int) -> str | None:
    """
    Decompress a zip file.
    :param source: Source path (include filename) .
    :param target: Target path (**not** include filename).
    :param step: 0 -> find inner zip, 1 -> find txt
    :return: Filename if found, None otherwise.
    :raise zipfile.BadZipFile: If zip file cannot be decompressed.
    :raise ValueError: Invalid step count.
    """
    if step not in [0, 1]:
        raise ValueError("Invalid step count. It must be 0 or 1.")

    with zipfile.ZipFile(file=source, mode="r") as zf:
        for name in zf.namelist():
            if name.startswith("bugreport") and name.endswith((".zip", ".txt")[step]):
                zf.extract(name, target)
                return name

    return None


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
                step = 0
                while step <= 1:
                    decompressed_filename = decompress(source=current_path, target=temp_dir, step=step)
                    if decompressed_filename is None:
                        raise ValueError(f"Step {step}: No matching file found in {current_path}")

                    current_path = os.path.join(temp_dir, decompressed_filename)
                    step += 1

                shutil.copy2(src=current_path, dst=self.final_path)
                return os.path.join(self.final_path, decompressed_filename)
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
