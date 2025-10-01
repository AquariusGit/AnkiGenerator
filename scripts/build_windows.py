#!/usr/bin/env python3
"""
Windows build script for AnkiGenerator
"""

import shutil
from pathlib import Path
from build_platform import run_build

def cleanup_pyside6_windows(app_dist_dir: Path):
    """
    Removes unnecessary files and folders from the PySide6 directory in the
    PyInstaller distribution to reduce the final package size.
    """
    pyside6_dir = app_dist_dir / "_internal" / "PySide6"
    if not pyside6_dir.is_dir():
        print(f"Warning: PySide6 directory not found at {pyside6_dir}. Skipping cleanup.")
        return

    print(f"Cleaning up PySide6 directory at: {pyside6_dir}")

    # Whitelist of files and folders to keep.
    # All other files/folders in PySide6 will be deleted.
    files_to_keep = {
        "pyside6.abi3.dll",
        "MSVCP140.dll", "MSVCP140_1.dll","MSVCP140_2.dll",
        "VCRUNTIME140.dll","VCRUNTIME140_1.dll",
                
        # Core Qt DLLs
        "Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", "Qt6UiTools.dll",
        "Qt6OpenGL.dll","Qt6OpenGLWidgets.dll",
        # Core .pyd modules
        "QtCore.pyd", "QtGui.pyd", "QtWidgets.pyd" ,"QtUiTools.pyd",
        "QtOpenGL.pyd","QtOpenGLWidgets.pyd",
        # Other necessary files
        "__init__.py", "qml.py",
    }
    
    folders_to_keep = {
        "plugins", # Contains platforms, styles, etc.
        "translations", # Contains translation files
    }

    for item in pyside6_dir.iterdir():
        if item.is_dir():
            if item.name not in folders_to_keep:
                print(f"  - Removing directory: {item.name}")
                shutil.rmtree(item)
        elif item.is_file():
            if item.name not in files_to_keep:
                print(f"  - Removing file: {item.name}")
                item.unlink()
    
    print("PySide6 cleanup complete.")

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    platform_args = [
        f"--icon={project_root / 'images' / 'icons' / 'windows.ico'}",
    ]
    
    run_build(
        platform_name="Windows",
        project_root=project_root,
        platform_specific_args=platform_args,
        pyside_cleanup_func=cleanup_pyside6_windows,
        get_app_dir_func=lambda dist_dir: dist_dir / "AnkiGenerator"
    )

if __name__ == "__main__":
    main()