#!/usr/bin/env python3
"""
macOS build script for AnkiGenerator
"""

import shutil
from pathlib import Path
from build_platform import run_build

def cleanup_pyside6_macos(app_bundle_path: Path):
    """
    Removes unnecessary files and folders from the PySide6 directory in the
    PyInstaller distribution to reduce the final package size on macOS.
    """
    # The _internal folder is inside Contents/MacOS for .app bundles
    pyside6_dir = app_bundle_path / "Contents" / "MacOS" / "_internal" / "PySide6"
    if not pyside6_dir.is_dir():
        print(f"Warning: PySide6 directory not found at {pyside6_dir}. Skipping cleanup.")
        return

    print(f"Cleaning up PySide6 directory at: {pyside6_dir}")

    # Whitelist of files and folders to keep.
    files_to_keep = {
        # Core .so modules (yes, .so on macOS for python extensions)
        "QtCore.so", "QtGui.so", "QtWidgets.so" ,"QtUiTools.so",
        "QtOpenGL.so","QtOpenGLWidgets.so",
        
        # Core Qt .dylib frameworks
        "QtOpenGL.framework", "QtOpenGLWidgets.framework",
        "QtCore.framework", "QtGui.framework", "QtWidgets.framework", "QtUiTools.framework",
        
        # Other necessary files
        "__init__.py", "qml.py", "pyside6.abi3.so",
    }
    
    folders_to_keep = {
        "plugins", # Contains platforms (libqcocoa.dylib), styles, etc.
        "translations",
    }

    for item in pyside6_dir.iterdir():
        if item.is_dir():
            # Frameworks are directories but we treat them like files to keep whole
            if item.name not in folders_to_keep and item.name not in files_to_keep:
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
        f"--icon={project_root / 'images' / 'icons' / 'macos.icns'}",
    ]

    run_build(
        platform_name="macOS",
        project_root=project_root,
        platform_specific_args=platform_args,
        pyside_cleanup_func=cleanup_pyside6_macos,
        get_app_dir_func=lambda dist_dir: dist_dir / "AnkiGenerator.app",
        get_copy_target_func=lambda app_dir: app_dir / "Contents" / "Resources"
    )

if __name__ == "__main__":
    main()
