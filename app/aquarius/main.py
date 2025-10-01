import sys
import os
import time

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from PySide6.QtWidgets import QApplication, QTextEdit, QProgressBar, QWidget, QVBoxLayout, QTabWidget, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTranslator, QLocale, QCoreApplication, QEvent
from typing import Optional

from PySide6.QtGui import QShortcut, QKeySequence

import webbrowser
import time

# 本地导入
from ui.qt_progress import QtProgress
from ui.download_form import DownloadFormController
from ui.configuration_form import ConfigurationFormController
from ui.generate_from_csv_form import GenerateFromCsvFormController
from ui.generate_from_subtitle_form import GenerateFromSubtitleFormController
from service.resource_manager import get_app_config, load_config, clear_temp_files,find_resource_in_installed_folder,find_resource_in_exec_folder
from ui.helper import find_required_child
from service.progress import Progress


class Logger:
    def __init__(self, file_name="default.log", stream=sys.stdout):
        self.terminal = stream
        self.log = open(file_name, "a", encoding="utf-8")

    def write(self, message):

        if self.terminal is not None:
            self.terminal.write(message)
        
        self.log.write(message)

    def flush(self):
        # 必须实现 flush 方法以兼容 print()
        pass  


class Application(QApplication):

    def __init__(self, argv):

        super().__init__(argv)
        
        if getattr(sys, 'frozen', False):
            self.redirect_stdout_to_log()

        self.translator : Optional[QTranslator] = None

        self.app_config = get_app_config()
        load_config(self.app_config)

        # 检查 cookies.txt 文件是否存在，如果存在则启用自动字幕功能
        self.app_config.support_auto_caption = False
        cookies_file_path = find_resource_in_installed_folder("cookies.txt")

        if os.path.exists(cookies_file_path):
            # 如果cookies.txt 文件的修改时间 >6个小时，则提示用户更新
            last_modified_time = os.path.getmtime(cookies_file_path)
            current_time = time.time()
            self.app_config.support_auto_caption = True
            
            if current_time - last_modified_time > 6 * 60 * 60:
                # 弹出对话框 提示用户更新cookies.txt文件 并询问是否继续使用
                title:str = QCoreApplication.translate("main","Cookies file outdated.")
                text:str = QCoreApplication.translate("main","Detected that the cookies.txt file has not been updated for more than 6 hours, which may prevent downloading protected subtitles normally. Do you want to continue?")
                
                reply = QMessageBox.question(
                    None,
                    title,
                    text,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.No:
                    sys.exit(0)                
            
        selected_language = self.load_translator(self.app_config.language)

        self.setStyle("Fusion")
        
        self.loader = QUiLoader()
        self.window = self.loader.load(find_resource_in_exec_folder("qt_ui/main.ui"))        

        self.setup_shortcuts()

        if not self.window:
            print(QCoreApplication.translate("main", "Failed to load main window UI file."))
            sys.exit(-1)

        # Get the tab widget from the main window
        self.main_tab: QTabWidget = find_required_child(self.window,QTabWidget, "main_tab")
        if not self.main_tab:
            sys.exit(-1)

        # Load the four sub-UIs into their respective tab pages       

        self.ui_files = [
            find_resource_in_exec_folder("qt_ui/download_form.ui"),
            find_resource_in_exec_folder("qt_ui/generate_from_subtitle_form.ui"),
            find_resource_in_exec_folder("qt_ui/generate_from_csv_form.ui"),
            find_resource_in_exec_folder("qt_ui/configuration_form.ui")
        ]

        for i, ui_file in enumerate(self.ui_files):
            self._load_ui_to_tab(self.loader, ui_file, self.main_tab, i)
                
        self.main_progressbar: QProgressBar = find_required_child(self.window,QProgressBar, "main_progressbar")
        self.log_edit: QTextEdit = find_required_child(self.window,QTextEdit, "log_edit")

        self.progress: Progress = QtProgress(self.main_progressbar, self.log_edit)

        self.download_form: QWidget = find_required_child(self.main_tab.widget(0),QWidget, "download_form")  # Get the actual form widget
        self.generate_from_subtitle_form: QWidget = find_required_child(self.main_tab.widget(1),QWidget, "generate_from_subtitle_form")  # Get the actual form widget
        self.generate_from_csv_form: QWidget = find_required_child(self.main_tab.widget(2),QWidget,"generate_from_csv_form")  # Get the actual form widget
        self.configuration_form: QWidget = find_required_child(self.main_tab.widget(3),QWidget, "configuration_form")

        self.configuration_form_controller = ConfigurationFormController(self.configuration_form, self.progress)
        self.download_form_controller = DownloadFormController(self.download_form, self.progress)
        self.generate_from_subtitle_form_controller = GenerateFromSubtitleFormController(self.generate_from_subtitle_form, self.progress)
        self.generate_from_csv_form_controller = GenerateFromCsvFormController(self.generate_from_csv_form, self.progress)

        # 连接 DownloadFormController 的信号到 Application 的转发方法
        self.download_form_controller.request_generate_from_subtitle.connect(self.forward_generate_from_subtitle)
        
        # 连接语言改变信号到处理槽
        self.configuration_form_controller.language_changed.connect(self.handle_language_change)

        # Connect cleanup function to aboutToQuit signal
        self.aboutToQuit.connect(clear_temp_files)

        # Set window size and show
        self.window.resize(960, 720)
        self.window.show()

    def forward_generate_from_subtitle(self, subtitle_config):
        """将信号转发给 GenerateFromSubtitleFormController"""
        self.main_tab.setCurrentIndex(1)
        self.generate_from_subtitle_form_controller.sync_subtitle_config_to_widget(subtitle_config)

    def _load_ui_to_tab(self, loader, ui_file, tab_widget, tab_index):
        """Loads a UI file into the specified tab page."""
        tab_page = tab_widget.widget(tab_index)
        ui = loader.load(ui_file, tab_page)
        if not ui:
            return False

        # Add the loaded UI to the tab page's layout
        layout = tab_page.layout()
        if not layout:
            layout = QVBoxLayout(tab_page)
            tab_page.setLayout(layout)
        layout.addWidget(ui)
        return True
    
    def handle_language_change(self, language_code):
        pass
        """处理语言改变的槽函数"""
        # 重新加载翻译文件
        # self.load_translator(language_code)

        # self.sendEvent(self.window, QEvent(QEvent.LanguageChange))

        # 询问用户是否需要重新启动程序以应用语言更改
        reply = QMessageBox.question(
            self.window,
            QCoreApplication.translate("main","Restart Required"),  # 或者使用翻译版本
            QCoreApplication.translate("main","The language change will take effect after restarting the application. Do you want to restart now?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.restart_application()

    def restart_application(self):
        """重新启动应用程序"""
        # 使用当前的Python解释器和命令行参数重新启动程序
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    # 在 Application 类中添加以下方法
    def load_translator(self, language_code: Optional[str] = None):
        """
        加载翻译文件，支持语言降级策略
        :param language_code: 指定语言代码，如不指定则使用系统语言
        """
        if not language_code:
            language_code = QLocale.system().name()  # 获取系统语言
        
        # 尝试的语言列表：指定语言 -> 语言基础版本 -> 英语默认版本
        language_attempts = [
            language_code,                    # 完整语言代码 (如 zh_CN)
            language_code.split('_')[0],     # 基础语言代码 (如 zh)
            'en'                             # 默认英语
        ]
        
        # 移除重复项但保持顺序
        seen = set()
        language_attempts = [x for x in language_attempts if not (x in seen or seen.add(x))]
        
        # 尝试加载翻译文件
        for lang in language_attempts:
            translator_file = f"translations/{lang}.qm"
            translator_file = find_resource_in_exec_folder(translator_file)

            if os.path.exists(translator_file):
                if self.translator:
                    self.removeTranslator(self.translator)
                
                self.translator = QTranslator()
                if self.translator.load(translator_file):
                    self.installTranslator(self.translator)
                    print(f"Successfully loaded translator: {lang}")
                    return lang
                else:
                    print(f"Failed to load translator: {lang}")
        
        print("No suitable translator found, using default English")
        return 'en'
    
    def setup_shortcuts(self):
        """设置F1快捷键打开帮助文档"""
        shortcut = QShortcut(QKeySequence("F1"), self.window)
        shortcut.activated.connect(self.open_help_url)
    

    def open_help_url(self):
        """打开帮助文档URL"""
        current_lang_code = get_app_config().language
        
        # Map UI language codes to HTML file suffixes
        lang_to_file_suffix = {
            "en": "en",
            "zh-hans": "zh_hans",
            "zh-hant": "zh_hant",
            "zh-cn": "zh_hans",
            "zh-tw": "zh_hant",
            "zh-hk": "zh_hant",
            "zh_cn": "zh_hans",
            "zh_tw": "zh_hant",
            "zh_hk": "zh_hant",
            "ja": "ja",
            "ko": "ko",
            "vi": "vi"
        }
        
        file_suffix = lang_to_file_suffix.get(current_lang_code.lower(), "en") # Default to "en" if not found
        
        def find_help_file(relative_path) -> Optional[str]:
            # 先用 find_resource_in_installed_folder 找
            path = find_resource_in_installed_folder(relative_path)
            if os.path.exists(path):
                return path
            # 如果找不到，再用 find_resource_in_exec_folder 找
            path = find_resource_in_exec_folder(relative_path)
            if os.path.exists(path):
                return path

            path = find_resource_in_installed_folder("../../"+relative_path)
            if os.path.exists(path):
                return path
            # 如果找不到，再用 find_resource_in_exec_folder 找
            path = find_resource_in_exec_folder("../../"+relative_path)
            if os.path.exists(path):
                return path
            
            return None

        lang_help_file = f"help/help_{file_suffix}.html"
        default_help_file = "help/help.html"

        # 优先查找语言特定的帮助文件，然后是默认的帮助文件
        file_to_open = find_help_file(lang_help_file) or find_help_file(default_help_file)
                    
        try:
            if file_to_open:
                file_to_open=os.path.normpath(file_to_open)
                webbrowser.open(file_to_open)
        except Exception as e:
            pass
   
    def redirect_stdout_to_log(self):
        # 重定向标准输出和错误输出到日志文件 文件格式为 UTF-8 文件名按日期命名
        log_dir = find_resource_in_installed_folder("logs")
        os.makedirs(log_dir, exist_ok=True)

        # 日志文件名按时间命名
        log_file = os.path.join(log_dir, f"log-{time.strftime('%Y%m%d')}.log")

        # 重定向标准输出和错误输出
        sys.stdout = Logger(log_file, sys.stdout)
        sys.stderr = Logger(log_file, sys.stderr)

if __name__ == "__main__":
    app = Application(sys.argv)
    sys.exit(app.exec())