#!/usr/bin/env python3
import os
import sys
from PySide6.QtCore import QProcess

def generate_ts_files():
    """生成 ts 语言包文件"""
    # 项目中所有包含需要翻译文本的源文件
    source_files = [
        "app/aquarius/main.py",
        "app/aquarius/qt_ui/main.ui",
        "app/aquarius/qt_ui/configuration_form.ui",
        "app/aquarius/qt_ui/download_form.ui",
        "app/aquarius/qt_ui/generate_from_csv_form.ui",
        "app/aquarius/qt_ui/generate_from_subtitle_form.ui",
        "app/aquarius/ui/base_from.py",
        "app/aquarius/ui/configuration_form.py",
        "app/aquarius/ui/download_form.py",
        "app/aquarius/ui/generate_from_csv_form.py",
        "app/aquarius/ui/generate_from_subtitle_form.py",
        "app/aquarius/ui/helper.py",
        "app/aquarius/ui/progress.py"
        "app/aquarius/service/generator.py",
        "app/aquarius/service/resource_manager.py",
        "app/aquarius/service/tts.py"
    ]

    for i, file in enumerate(source_files):
        file="app/"+ file
        source_files[i]=file
    
    # 需要支持的语言列表
    languages = ["en", "zh", "zh_CN","zh_TW","ja","ko"]
    
    # 生成 .ts 文件
    for lang in languages:
        ts_file = f"app/aquarius/translations/{lang}.ts"
        cmd = [
            "pyside6-lupdate",
            "-no-obsolete"
        ] + source_files + [
            "-ts",
            ts_file
        ]
        
        process = QProcess()
        process.start("pyside6-lupdate", cmd[1:])
        process.waitForFinished()
        
        if process.exitCode() == 0:
            print(f"Successfully generated {ts_file}")
        else:
            print(f"Failed to generate {ts_file}")
            print(process.readAllStandardError().data().decode())

if __name__ == "__main__":
    generate_ts_files()