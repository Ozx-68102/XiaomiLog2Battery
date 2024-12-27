import subprocess
import sys


def check_and_install_packages():
    required_packages = ['pyecharts', 'pandas']
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package} is already installed.")
        except ImportError:
            print(f"{package} is not installed. So installation will begin soon...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip3", "install", package])
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}. Please check your internet connection or Python environment.")
                sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    check_and_install_packages()