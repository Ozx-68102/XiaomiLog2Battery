import subprocess
import sys


def check_and_install_packages():
    required_packages = [
        "pyecharts", "pandas", "plotly", "dash", "dash-bootstrap-components", "json"
    ]
    count = 0
    for package in required_packages:
        try:
            __import__(package)
            print(f"{count + 1}. {package} is already installed.")
        except ImportError:
            try:
                result = subprocess.run(args=[sys.executable, "-m", "pip", "show", package], stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
                if result.returncode == 0:
                    print(f"{count + 1}. {package} is already installed.")
                else:
                    raise subprocess.CalledProcessError(result.returncode, result.args)
            except subprocess.CalledProcessError:
                try:
                    print(f"{count + 1}. {package} is not installed. So installation will begin soon...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                except subprocess.CalledProcessError:
                    print(f"Failed to install {package}. Please check your internet connection or Python environment.")
                    sys.exit(1)

        count += 1

    sys.exit(0)


if __name__ == "__main__":
    check_and_install_packages()
