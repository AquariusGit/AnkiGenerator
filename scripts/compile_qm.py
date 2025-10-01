#!/usr/bin/env python3
import os
from PySide6.QtCore import QProcess

def compile_qm_files():
    """编译 ts 文件为 qm 文件"""
    ts_dir = "app/aquarius/translations/"
    
    if not os.path.exists(ts_dir):
        print(f"Directory {ts_dir} does not exist")
        return
    
    for file in os.listdir(ts_dir):
        if file.endswith(".ts"):
            ts_file = os.path.join(ts_dir, file)
            qm_file = os.path.join(ts_dir, file.replace(".ts", ".qm"))
            
            process = QProcess()
            process.start("lrelease", [ts_file, "-qm", qm_file])
            process.waitForFinished()
            
            if process.exitCode() == 0:
                print(f"Successfully compiled {ts_file} to {qm_file}")
            else:
                print(f"Failed to compile {ts_file}")
                print(process.readAllStandardError().data().decode())

if __name__ == "__main__":
    compile_qm_files()