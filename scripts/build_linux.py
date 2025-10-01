#!/usr/bin/env python3
"""
Linux build script for AnkiGenerator
"""

import shutil
from pathlib import Path
from build_platform import run_build

def cleanup_pyside6_linux(app_dist_dir: Path):
    """
    Removes unnecessary files and folders from the PySide6 directory in the
    PyInstaller distribution to reduce the final package size on Linux.
    """
    pyside6_dir = app_dist_dir / "_internal" / "PySide6"
    if not pyside6_dir.is_dir():
        print(f"Warning: PySide6 directory not found at {pyside6_dir}. Skipping cleanup.")
        return

    print(f"Cleaning up PySide6 directory at: {pyside6_dir}")

    # Whitelist of files and folders to keep.
    files_to_keep = {
        # Core .so modules
        "QtCore.so", "QtGui.so", "QtWidgets.so" ,"QtUiTools.so",
        "QtOpenGL.so","QtOpenGLWidgets.so",
        # Other necessary files
        "__init__.py", "qml.py",
    }
    
    # Whitelist for glob patterns (for versioned .so files)
    glob_patterns_to_keep = [
        "libQt6Core.so*", "libQt6Gui.so*", "libQt6Widgets.so*", "libQt6UiTools.so*",
        "libQt6OpenGL.so*", "libQt6OpenGLWidgets.so*",
        "libpyside6.abi3.so*",
    ]

    folders_to_keep = {
        "plugins", # Contains platforms (libqxcb.so), styles, etc.
        "translations",
    }

    items_to_keep = set(files_to_keep)
    for pattern in glob_patterns_to_keep:
        items_to_keep.update(item.name for item in pyside6_dir.glob(pattern))

    for item in pyside6_dir.iterdir():
        if item.name in items_to_keep:
            continue
        if item.is_dir():
            if item.name not in folders_to_keep:
                print(f"  - Removing directory: {item.name}")
                shutil.rmtree(item)
        elif item.is_file():
            print(f"  - Removing file: {item.name}")
            item.unlink()
    
    print("PySide6 cleanup complete.")

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    platform_args = [
        # Icon for Linux is usually handled by .desktop files, but we can add it.
        # f"--icon={project_root / 'images' / 'icons' / 'linux.png'}",
    ]

    run_build(
        platform_name="Linux",
        project_root=project_root,
        platform_specific_args=platform_args,
        pyside_cleanup_func=cleanup_pyside6_linux,
        get_app_dir_func=lambda dist_dir: dist_dir / "AnkiGenerator"
    )

if __name__ == "__main__":
    main()
