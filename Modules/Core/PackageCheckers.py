import os
import subprocess
import sys


def get_package_version(package: str) -> str | bool:
    """
    Check package version.
    :param package: package name
    :return: Installed => str, Cannot find version => True, Not installed => False
    """
    try:
        result = subprocess.run(args=[sys.executable, "-m", "pip", "show", package], capture_output=True, text=True,
                                check=True)
        for line in result.stdout.split("\n"):
            if line.startswith("Version"):
                return line.split(":")[1].strip()

        return True
    except subprocess.CalledProcessError:
        return False


def install_package(package: str, version: str | None = None, local_path: str | None = None) -> None:
    # Modified to support local installation
    if local_path:
        # Use --force-reinstall to ensure the local version overwrites any existing one
        args = [sys.executable, "-m", "pip", "install", local_path, "--force-reinstall"]
    else:
        name = f"{package}=={version}" if version else package
        args = [sys.executable, "-m", "pip", "install", name]

    subprocess.check_call(args=args)


def check_and_install_packages() -> None:
    # Calculate the path to the libs folder
    # Structure: Root/Modules/Core/PackageCheckers.py -> Need to go up 3 levels
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    whl_path = os.path.join(base_dir, "libs", "dash_uploader-0.7.0a2+fix2-py3-none-any.whl")

    required_packages = {
        # Use a tuple or dict to specify version and local path
        "dash-uploader": {"ver": "0.7.0a2+fix2", "path": whl_path},
        "pandas": None,
        "plotly": None,
        "dash": "3.3.0",
        "waitress": "3.0.2",
        "dash-bootstrap-components": "2.0.4",
        "werkzeug": "3.1.3" # 3.1.4 import a bug that cause UPLOADED FILE ERROR
    }

    counts = 0
    success = 0
    failed = 0

    for required_package, spec in required_packages.items():
        # Parse version and path from spec
        local_path = None

        if isinstance(spec, dict):
            specified_version = spec.get("ver")
            local_path = spec.get("path")
        else:
            specified_version = spec

        try:
            if not specified_version:
                status = get_package_version(required_package)

                # Package installed
                if isinstance(status, str) or status is True:
                    print(f"{counts + 1}. {required_package} is already installed.")
                    counts += 1
                    success += 1
                    continue

                # Package not install
                print(f"{counts + 1}. {required_package} is not installed. So installation will begin soon...")
                install_package(required_package)
                counts += 1
                success += 1
                continue

            # Specified package version
            version = get_package_version(required_package)

            # Version incorrect
            if version != specified_version:
                print(
                    f"{counts + 1}. {required_package} version incorrect or not installed. So installation will begin soon...")
                install_package(required_package, specified_version, local_path)  # Pass local_path
                counts += 1
                success += 1
                continue

            # Version correct
            print(f"{counts + 1}. {required_package} is already installed.")
            counts += 1
            success += 1
            continue
        except subprocess.CalledProcessError as e:
            print(f"{counts + 1}. Failed to install {required_package}: {e}")
            counts += 1
            failed += 1
            continue

    print(f"Completed. Success: {success}. Failed: {failed}. Total: {counts}.")
    exit_code = 1 if failed > 0 else 0
    sys.exit(exit_code)


if __name__ == "__main__":
    check_and_install_packages()