import subprocess
import sys
from pathlib import Path

def create_venv(venv_path):
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)])

def install_requirements(venv_path):
    # Use sys.executable to get the Python interpreter path inside the virtual environment
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    # Set the path for the virtual environment
    venv_path = Path("venv")

    # Create the virtual environment
    create_venv(venv_path)

    # Activate the virtual environment
    activate_script = "Scripts/activate" if sys.platform == "win32" else "bin/activate"
    activate_path = venv_path / activate_script
    print(f"\nActivate the virtual environment by running: {activate_path}\n")

    # Install the requirements
    install_requirements(venv_path)

if __name__ == "__main__":
    main()
