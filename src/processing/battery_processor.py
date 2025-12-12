import shutil
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor, Future
from pathlib import Path

from src.config import INSTANCE_PATH, TXT_PATH


def decompress(source: str | Path, target: str | Path, step: int) -> str | None:
    """
    Decompress a zip file.

    Parameters
    ----------
    source: str or Path
        Source path (include filename).
    target: str or Path
        Target path (not include filename).
    step: 0 or 1
        0 -> find inner zip, 1 -> find txt

    Raises
    ------
    ValueError
        Invalid step count.
    zipfile.BadZipFile
        Invalid zip file.

    Returns
    -------
    str | None
        Filename if found, None otherwise.
    """
    if step not in (0, 1):
        raise ValueError("Invalid step count. It must be 0 or 1.")

    with zipfile.ZipFile(file=source, mode="r") as zf:
        for name in zf.namelist():
            if name.startswith("bugreport") and name.endswith((".zip", ".txt")[step]):
                zf.extract(name, target)
                return name

    return None


class BatteryProcessor:
    def __init__(self) -> None:
        self.top_temp = INSTANCE_PATH / "temp"

        if self.top_temp.exists():
            shutil.rmtree(self.top_temp, ignore_errors=True)

        self.top_temp.mkdir(exist_ok=True)

        self.final_path = TXT_PATH
        self.final_path.mkdir(exist_ok=True)

    def _extract_single_log(self, fp: str | Path) -> Path:
        """
        Extract a Xiaomi log file from a specified Xiaomi zip file.

        Parameters
        ----------
        fp: str or Path
            Path of Xiaomi zip file.

        Returns
        -------
        Path
            A Path object containing the Xiaomi log filepath.
        """
        path = Path(fp)

        if not path.is_file():
            raise ValueError(f"Variable '{fp}' is not a valid file.")

        if not path.stem.startswith("bugreport") or path.suffix != ".zip":
            raise ValueError(f"'{path.name}' not a valid Xiaomi zip file.")

        with tempfile.TemporaryDirectory(dir=self.top_temp, prefix="temp-") as td:
            temp_path = Path(td)

            try:
                current_path = path
                step = 0
                while step <= 1:
                    decompress_name = decompress(source=current_path, target=temp_path, step=step)
                    if decompress_name is None:
                        raise ValueError(f"Step {step}: No matching file found in {current_path}")

                    current_path = temp_path / decompress_name
                    step += 1

                shutil.copy2(src=current_path, dst=self.final_path)
                return self.final_path / decompress_name

            except Exception as e:
                raise RuntimeError(f"Failed to process {path.name}: {e}")

    def process_xiaomi_log(self, fps: list[str], thread_count: int) -> list[Path]:
        """
        Process or extract one or more Xiaomi log files from zip files.

        Parameters
        ----------
        fps: list[str]
            A list of Xiaomi zip file paths.
        thread_count: int
            Number of worker threads/processes.

        Returns
        -------
        list[Path]
            A list of extracted Xiaomi log files.
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
            futures: list[Future[Path]] = [executor.submit(self._extract_single_log, file) for file in fps]

            for future in futures:
                try:
                    results = future.result()
                    if results:
                        final_paths.append(Path(results))
                except Exception as e:
                    print(e)
                    continue

        return final_paths


if __name__ == "__main__":
    pass
