#!/usr/bin/env python3
"""
Common build functions for AnkiGenerator across different platforms.
This script is not meant to be run directly but imported by platform-specific build scripts.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Callable, Optional


def prepare_build_environment(project_root: Path):
    """Cleans up previous build artifacts and ensures PyInstaller is installed."""
    print("Preparing build environment...")

    # Change to the project root directory
    os.chdir(project_root)

    # Clean up dist and build directories
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def get_pykakasi_path() -> str:
    """Locates and returns the path to pykakasi's data files."""
    try:
        import pkg_resources
        return pkg_resources.resource_filename('pykakasi', 'data')
    except (ImportError, ModuleNotFoundError):
        print("Warning: pkg_resources not found or pykakasi not installed. The build might fail to include pykakasi data.")
        return ""


def copy_additional_directories(target_dir: Path, project_root: Path):
    """
    Copies 'examples' directory, only HTML files from the 'help' directory,
    and creates a default 'help.html' from 'help_en.html'.
    """
    print(f"Copying additional directories to: {target_dir}")

    # Copy only .html files from the 'help' directory
    src_help_dir = project_root / "help"
    if src_help_dir.is_dir():
        dst_help_dir = target_dir / "help"
        dst_help_dir.mkdir(exist_ok=True)
        for file in src_help_dir.glob("*.html"):
            shutil.copy(file, dst_help_dir)
        print("  - Copied HTML files from 'help' directory.")

        # Create a default help.html from the English version
        default_help_src = dst_help_dir / "help_en.html"
        if default_help_src.exists():
            shutil.copy(default_help_src, dst_help_dir / "help.html")
            print("  - Created default 'help.html' from 'help_en.html'.")

    # Copy the entire 'examples' directory
    src_examples_dir = project_root / "examples"
    if src_examples_dir.is_dir():
        dst_examples_dir = target_dir / "examples"
        if dst_examples_dir.exists():
            shutil.rmtree(dst_examples_dir)
        shutil.copytree(src_examples_dir, dst_examples_dir)
        print("  - Copied 'examples' directory.")


def run_build(
    platform_name: str,
    project_root: Path,
    platform_specific_args: List[str],
    pyside_cleanup_func: Callable[[Path], None],
    get_app_dir_func: Callable[[Path], Path],
    get_copy_target_func: Optional[Callable[[Path], Path]] = None
):
    """
    Runs the full PyInstaller build and cleanup process.
    """
    print(f"Building AnkiGenerator for {platform_name}...")
    prepare_build_environment(project_root)

    pykakasi_data_path = get_pykakasi_path()

    # Common PyInstaller command parts
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--clean",
        "--name", "AnkiGenerator",
        f"--add-data=app/aquarius/qt_ui{os.pathsep}qt_ui",
        f"--add-data=app/aquarius/translations{os.pathsep}translations",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtUiTools",
        "--hidden-import", "pykakasi",
        "--hidden-import", "pykakasi.kakasi",
        "--hidden-import", "pykakasi.constants",
        "--hidden-import", "pykakasi.utils",
        "--hidden-import", "pykakasi.cli",
        "--hidden-import", "pykakasi.data",
        "--hidden-import", "pykakasi.dictionary",
        f"--add-data={pykakasi_data_path}{os.pathsep}pykakasi/data",
        "--exclude-module", "numpy",
    ] + platform_specific_args + ["app/aquarius/main.py"]

    print("\nRunning PyInstaller with command:")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True, text=True)
    print("\nPyInstaller build completed successfully!")

    app_dir = get_app_dir_func(project_root / "dist")
    pyside_cleanup_func(app_dir)

    if get_copy_target_func:
        copy_target_dir = get_copy_target_func(app_dir)
        copy_additional_directories(copy_target_dir, project_root)
    else:
        copy_additional_directories(app_dir, project_root)

    shutil.rmtree(project_root / "build")
    print("Cleaned up build directory.")
    print(f"\nBuild process finished. Artifacts are in: {app_dir}")