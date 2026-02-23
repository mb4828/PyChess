#!/usr/bin/env python3
"""Build script for PGChess. Creates single-file executables for Windows and macOS."""
import logging
import os
import platform
import shutil
import subprocess
import sys

logger = logging.getLogger(__name__)


def clean_build() -> None:
    """Remove old build artifacts from previous PyInstaller runs."""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['PGChess.spec']

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            logger.info("Removing %s/", dir_name)
            shutil.rmtree(dir_name)

    for file_name in files_to_remove:
        if os.path.exists(file_name):
            logger.info("Removing %s", file_name)
            os.remove(file_name)


def build_windows() -> None:
    """Build a single-file Windows executable using PyInstaller."""
    logger.info("Building for Windows...")
    cmd = [
        'pyinstaller',
        '--onefile',
        'main.py',
        '--paths', 'venv/Lib/site-packages',
        '--add-data', 'assets/images/*;assets/images',
        '--add-data', 'assets/sounds/*;assets/sounds',
        '--add-data', 'venv/Lib/site-packages/pygame_menu/resources/fonts/*;pygame_menu/resources/fonts',
        '--name', 'PGChess',
        '--icon', 'assets/images/pgchess.ico',
        '--noconsole',
    ]
    subprocess.run(cmd, check=True)
    logger.info("Build complete! Executable is in dist/PGChess.exe")


def build_macos() -> None:
    """Build a macOS .app bundle using PyInstaller."""
    logger.info("Building for macOS...")
    cmd = [
        'pyinstaller',
        '--windowed',
        'main.py',
        '--paths', 'venv/lib/python3.11/site-packages',
        '--add-data', 'assets/images/*:assets/images',
        '--add-data', 'assets/sounds/*:assets/sounds',
        '--add-data', 'venv/lib/python3.11/site-packages/pygame_menu/resources/fonts/*:pygame_menu/resources/fonts',
        '--name', 'PGChess',
        '--icon', 'assets/images/pgchess.png',
    ]
    subprocess.run(cmd, check=True)

    # PyInstaller creates both a COLLECT folder and a .app bundle; only the .app is needed
    standalone_folder = 'dist/PGChess'
    if os.path.exists(standalone_folder) and os.path.isdir(standalone_folder):
        shutil.rmtree(standalone_folder)
        logger.info("Cleaned up %s/ folder", standalone_folder)

    logger.info("Build complete! App bundle is in dist/PGChess.app")


def main() -> None:
    """Detect the current platform and run the appropriate build."""
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    system = platform.system()
    logger.info("PGChess Build Script")
    logger.info("Platform: %s", system)
    logger.info("-" * 50)

    clean_build()

    if system == 'Windows':
        build_windows()
    elif system == 'Darwin':
        build_macos()
    else:
        logger.error(
            "Unsupported platform '%s'. This script supports Windows and macOS only.", system)
        sys.exit(1)


if __name__ == '__main__':
    main()
