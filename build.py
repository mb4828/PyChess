#!/usr/bin/env python3
"""
Build script for PyChess
Creates single-file executables for Windows and macOS
"""
import os
import sys
import shutil
import subprocess
import platform


def clean_build():
    """Remove old build artifacts"""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['PyChess.spec']

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}/")
            shutil.rmtree(dir_name)

    for file_name in files_to_remove:
        if os.path.exists(file_name):
            print(f"Removing {file_name}")
            os.remove(file_name)


def build_windows():
    """Build for Windows"""
    print("Building for Windows...")
    cmd = [
        'pyinstaller',
        '--onefile',
        'main.py',
        '--paths', 'venv/Lib/site-packages',
        '--paths', 'game/',
        '--paths', 'logic/',
        '--add-data', 'assets/images/*;assets/images',
        '--add-data', 'assets/sounds/*;assets/sounds',
        '--add-data', 'venv/Lib/site-packages/pygame_menu/resources/fonts/*;pygame_menu/resources/fonts',
        '--name', 'PyChess',
        '--icon', 'assets/images/pychess.ico',
        '--noconsole'
    ]
    subprocess.run(cmd, check=True)
    print("\nBuild complete! Executable is in dist/PyChess.exe")


def build_macos():
    """Build for macOS"""
    print("Building for macOS...")
    cmd = [
        'pyinstaller',
        '--windowed',
        'main.py',
        '--paths', 'venv/lib/python3.11/site-packages',
        '--paths', 'game/',
        '--paths', 'logic/',
        '--add-data', 'assets/images/*:assets/images',
        '--add-data', 'assets/sounds/*:assets/sounds',
        '--add-data', 'venv/lib/python3.11/site-packages/pygame_menu/resources/fonts/*:pygame_menu/resources/fonts',
        '--name', 'PyChess',
        '--icon', 'assets/images/pychess.ico'
    ]
    subprocess.run(cmd, check=True)

    # Remove the standalone folder (we only want the .app bundle)
    standalone_folder = 'dist/PyChess'
    if os.path.exists(standalone_folder) and os.path.isdir(standalone_folder):
        shutil.rmtree(standalone_folder)
        print(f"Cleaned up {standalone_folder}/ folder")

    print("\nBuild complete! App bundle is in dist/PyChess.app")
    print("You can drag PyChess.app to your Applications folder or double-click to run.")


def main():
    """Main build function"""
    system = platform.system()

    print(f"PyChess Build Script")
    print(f"Platform: {system}")
    print("-" * 50)

    # Clean previous builds
    clean_build()

    # Build for the current platform
    if system == 'Windows':
        build_windows()
    elif system == 'Darwin':  # macOS
        build_macos()
    else:
        print(f"Error: Unsupported platform '{system}'")
        print("This script supports Windows and macOS only.")
        sys.exit(1)


if __name__ == '__main__':
    main()
