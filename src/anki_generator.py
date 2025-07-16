import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import json
import os
import logging
import re
import threading
from urllib.parse import urlparse
import subprocess
import sys
import csv
import webbrowser
import random
import glob # Added for robust subtitle file detection
import asyncio # Moved to top for consistent import
from dataclasses import dataclass, field  
from helper import Start
from tooltip import ToolTip, ComboboxSearch
from localization import (
    get_locale_string as _,
    set_language,
    get_lang_display,
    get_available_languages,
    get_available_display_languages
)

@dataclass
class AnkiConfig:
    """数据类，用于存储Anki包生成配置"""
    source_type: str= field(init=False)
    anki_package_name: str = field(init=False)
    csv_file: str = field(init=False)
    media_file: str = field(init=False)
    output_dir: str= field(init=False)
    screenshot_time: str= field(init=False)
    add_ruby_front: bool= True
    add_ruby_back: bool= True
    slow_front: bool= False
    slow_back: bool= False
    cleanup_mp3: bool= True
    cleanup_csv: bool= True
    cleanup_jpg: bool= True
    cleanup_preview_html: bool= True
    overwrite_apkg: bool= True
    tts_engine: str= "edge-tts"
    add_screenshot: bool= False
    extract_audio_segment: bool= True
    timeline_offset_ms: int= 0
    screenshot_quality:int=1
    merge_subtitles:bool= False
    merge_gap_ms: int= 0
    clean_subtitle:bool= False
    start_time_str:str= field(init=False)
    end_time_str:str= field(init=False)
    

# 添加剪贴板支持
import pyperclip

# 添加yt-dlp支持
import yt_dlp

# 添加字幕处理支持
import pysrt

# 添加音频处理支持
from pydub import AudioSegment

# 添加TTS支持
from gtts import gTTS

import edge_tts

# 添加Anki包生成支持
import genanki

# 添加日语注音支持
import pykakasi


from helper import add_furigana, add_pinyin, add_romanization_ko

class AnkiGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(("Anki Generator"))
        self.root.geometry("1200x800")

        self.defaultPreviewConfig={
            "anki_templates": {
                "front": "{{Question}}",
                "back": "{{Answer}}"
            },
            "anki_style": ".card {\n    font-family: arial;\n    font-size: 24px;\n    text-align: left;\n    color: black;\n    background-color: white;\n}",
        }
                
        # 配置信息
        self.config = {
            "download_directory": "",
            "anki_templates": {
                "front": "{{Question}}\n\n{{#Audio_Question}}\n\t{{Audio_Question}}\n{{/Audio_Question}} \n\n{{#Screenshot}} \n\t{{Screenshot}}\n{{/Screenshot}}",
                "back": "{{Answer}}\n\n{{#Audio_Answer}} \n\t{{Audio_Answer}}\n{{/Audio_Answer}}\n\n{{#Screenshot}} \n\t{{Screenshot}}\n{{/Screenshot}}"
            },
            "anki_style": ".card {\n    font-family: arial;\n    font-size: 24px;\n    text-align: left;\n    color: black;\n    background-color: white;\n}",
            "preferred_front_language": "",
            "preferred_back_language": "",
            "tts_engine": "gtts",
            "preview_html_template": """<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><title>Anki 卡片预览</title>
        <style>
            body { font-family: sans-serif; background-color: #f0f0f0; padding: 20px; }
            h1 { text-align: center; color: #333; }
            .card-container { background-color: #fff; border: 1px solid #ccc; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .card-side h3 { color: #777; font-size: 1em; margin-top: 0; }
            hr { border: 0; border-top: 1px solid #ddd; margin: 20px 0; }
            {{style}}
            .anki-back { display: block !important; }
            ruby rt { font-size: 0.7em; }
        </style></head><body><h1>Anki 卡片预览</h1>{{cards_html}}</body></html>""",
            "dont_validate_url": False
        }
        
        # 下载相关变量
        self.available_formats = []
        self.available_subtitles = []
        self.download_results = {}
        self.download_only_subtitles_var = tk.BooleanVar(value=False)
        
        # List to store preview files for cleanup on exit
        self.preview_files_to_cleanup = []
        
        # 支持的语言代码 (ISO 639-1)
        self.supported_languages = [
            "en", "zh-Hans", "zh-Hant", "ja", "ko", "fr", "de", "es", "it", "ru", "pt", "ar", "hi",
            "id", "tr", "vi", "pl", "nl", "th", "sv", "el", "hu", "cs", "ro", "fi",
            "da", "no"
        ]
        
        # Language setting
        self.current_lang = tk.StringVar(value="zh-Hans")

        # 加载配置
        self.load_config()
        if "language" in self.config:
            self.current_lang.set(self.config["language"])
        set_language(self.current_lang.get())

        self.root.title(_("app_title"))
        
        # 创建菜单栏
        self.create_menu()

        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 进度条在最下方
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        self.progress_label = ttk.Label(self.progress_frame, text=_("label_progress"))
        self.progress_label.pack(side=tk.LEFT, padx=5);
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 创建可调整窗格
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 选项卡控件在左侧窗格
        self.tab_control = ttk.Notebook(self.paned_window)
        self.paned_window.add(self.tab_control, weight=2)
        
        # 创建四个选项卡
        self.download_tab = ttk.Frame(self.tab_control)
        self.csv_tab = ttk.Frame(self.tab_control)
        self.anki_tab = ttk.Frame(self.tab_control)
        self.config_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.download_tab, text=_("tab_download"))
        self.tab_control.add(self.anki_tab, text=_("tab_generate"))
        self.tab_control.add(self.csv_tab, text=_("CSV_generate"))        
        self.tab_control.add(self.config_tab, text=_("tab_config"))
        
        # 绑定选项卡切换事件
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # 日志输出框在右侧窗格
        self.log_frame = ttk.LabelFrame(self.paned_window, text=_("label_log"))
        self.paned_window.add(self.log_frame, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, state='disabled', width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 设置日志处理器
        self.setup_logger()
        
        # 初始化各个选项卡的内容
        self.setup_download_tab()
        self.setup_csv_tab()
        self.setup_generate_tab()
        self.setup_config_tab()        
        
        # 程序关闭时保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 检查外部依赖
        # self.check_ffmpeg()

    def load_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 更新配置，保留默认值
                    for key in loaded_config:
                        if key in self.config:
                            self.config[key] = loaded_config[key]
                self.logger.info(_("log_config_loaded")) if hasattr(self, 'logger') else None
            except Exception as e:
                print(_("error_loading_config", e))

    def open_help_file(self):
        current_lang_code = self.current_lang.get()
        
        # Map UI language codes to HTML file suffixes
        lang_to_file_suffix = {
            "en": "en",
            "zh-Hans": "zh_hans",
            "zh-Hant": "zh_hant",
            "ja": "ja",
            "ko": "ko",
            "vi": "vi"
        }
        
        file_suffix = lang_to_file_suffix.get(current_lang_code, "en") # Default to "en" if not found
        
        help_file_name = f"help/help_{file_suffix}.html"
        default_help_file_name = "help.html" # This is the English version
        
        # Construct absolute paths
        # Assuming help files are in the same directory as anki_generator.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        help_file_path = os.path.join(base_dir, help_file_name)
        default_help_file_path = os.path.join(base_dir, default_help_file_name)
        
        file_to_open = ""
        if os.path.exists(help_file_path):
            file_to_open = help_file_path
            self.logger.info(f"Opening help file: {help_file_path}")
        elif os.path.exists(default_help_file_path):
            file_to_open = default_help_file_path
            self.logger.warning(f"Help file for language '{current_lang_code}' not found. Opening default help file: {default_help_file_path}")
        else:
            self.logger.error("Neither language-specific nor default help file found.")
            messagebox.showerror(_("error_title_help_not_found"), _("error_msg_help_not_found"))
            return
            
        try:
            webbrowser.open(file_to_open)
        except Exception as e:
            self.logger.error(f"Failed to open help file {file_to_open}: {e}")
            messagebox.showerror(_("error_title_open_help_failed"), _("error_msg_open_help_failed", file_to_open))

    def check_ffmpeg(self):
        """检查系统中是否安装了ffmpeg"""
        try:
            # 使用 -version 参数来检查，并将输出重定向到DEVNULL，避免在控制台打印信息
            subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.logger.info(_("log_ffmpeg_found"))
            return True
        except FileNotFoundError:
            self.logger.error(_("error_ffmpeg_not_found"))
            messagebox.showerror(_("error_title_dependency_missing"), _("error_msg_ffmpeg_not_found"))
            return False
        except subprocess.CalledProcessError:
            # 这通常意味着ffmpeg存在但执行时返回了错误，对于版本检查来说不太可能，但以防万一
            self.logger.error(_("error_ffmpeg_execution"))
            messagebox.showerror(_("error_title_dependency_error"), _("error_msg_ffmpeg_execution"))
            return False


    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        language_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("label_language"), menu=language_menu)

        for lang_code, lang_name in get_available_languages().items():
            language_menu.add_radiobutton(
                label=lang_name,
                variable=self.current_lang,
                value=lang_code,
                command=self.change_language
            )
        
        # Add Help menu item
        menubar.add_command(label=_("label_help"), command=self.open_help_file)

    def change_language(self):
        lang = self.current_lang.get()
        set_language(lang)
        self.config["language"] = lang
        self.update_ui_text()

    def update_ui_text(self):
        # 重新创建菜单以更新其语言
        self.create_menu()

        self.root.title(_("app_title"))
        self.tab_control.tab(self.download_tab, text=_("tab_download"))
        self.tab_control.tab(self.csv_tab, text=_("tab_csv"))
        self.tab_control.tab(self.anki_tab, text=_("tab_generate"))
        self.tab_control.tab(self.config_tab, text=_("tab_config"))
        self.progress_label.config(text=_("label_progress"))
        self.log_frame.config(text=_("label_log"))

        # Update download tab
        self.setup_download_tab()
        # Update csv tab
        self.setup_csv_tab()
        # Update generate tab
        self.setup_generate_tab()
        # Update config tab
        self.setup_config_tab()
    
    def setup_logger(self):
        # 创建日志处理器，将日志输出到文本框
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state='normal')
                    # 根据日志级别设置颜色
                    if record.levelno >= logging.ERROR:
                        self.text_widget.insert(tk.END, msg + '\n', "error")
                    else:
                        self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.configure(state='disabled')
                    self.text_widget.yview(tk.END)
                self.text_widget.after(0, append)
        
        # 配置日志
        self.logger = logging.getLogger('AnkiGenerator')
        self.logger.setLevel(logging.INFO)
        
        # 清除现有的处理器
        for handler in self.logger.handlers[:]: 
            self.logger.removeHandler(handler)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        text_handler.setFormatter(formatter)
        self.logger.addHandler(text_handler)
        
        # 为错误消息添加标签
        self.log_text.tag_configure("error", foreground="red")
        
        # 记录启动信息
        self.logger.info(_("log_app_started"))
    
    def setup_download_tab(self):
        # 下载选项卡内容
        # Clear existing widgets
        for widget in self.download_tab.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.download_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # URL输入
        ttk.Label(frame, text=_("label_video_url")).grid(column=0, row=0, sticky=tk.E, pady=2)
        url_input_frame = ttk.Frame(frame)
        url_input_frame.grid(column=1, row=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.url_entry = ttk.Entry(url_input_frame, width=40)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.bind("<Button-1>", lambda event: self.check_clipboard())
        self.query_button = ttk.Button(url_input_frame, text=_("button_query_language"), command=self.query_video_info)
        self.query_button.pack(side=tk.RIGHT, padx=5)

        self.dont_validate_url_var = tk.BooleanVar(value=self.config.get("dont_validate_url", False))
        self.dont_validate_url_check = ttk.Checkbutton(url_input_frame, text=_("check_dont_validate_url"), variable=self.dont_validate_url_var, command=self._update_dont_validate_url_config)
        self.dont_validate_url_check.pack(side=tk.RIGHT, padx=5)

        ToolTip(self.dont_validate_url_check, _("tooltip_dont_validate_url_check"))

        # 下载目录选择
        ttk.Label(frame, text=_("label_download_dir")).grid(column=0, row=1, sticky=tk.E, pady=2)  # 右对齐
        self.download_dir_frame = ttk.Frame(frame)
        self.download_dir_frame.grid(column=1, row=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.download_dir_entry = ttk.Entry(self.download_dir_frame, width=40)
        self.download_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.download_dir_entry.insert(0, self.config["download_directory"])
        self.browse_button = ttk.Button(self.download_dir_frame, text=_("button_browse"), command=self.browse_download_dir)
        self.browse_button.pack(side=tk.RIGHT, padx=5)

        # 音视频格式选择
        ttk.Label(frame, text=_("label_av_format")).grid(column=0, row=2, sticky=tk.E, pady=2)  # 右对齐
        self.format_combobox = ttk.Combobox(frame, width=40, state="readonly")
        ComboboxSearch(self.format_combobox)
        self.format_combobox.grid(column=1, row=2, sticky=(tk.W, tk.E), padx=5, pady=2)

        # 正面字幕语言选择
        ttk.Label(frame, text=_("label_front_sub_lang")).grid(column=0, row=3, sticky=tk.E, pady=2)  # 右对齐
        self.front_subtitle_combobox = ttk.Combobox(frame, width=40, state="readonly")
        ComboboxSearch(self.front_subtitle_combobox)
        self.front_subtitle_combobox.grid(column=1, row=3, sticky=(tk.W, tk.E), padx=5, pady=2)

        # 背面字幕语言选择
        ttk.Label(frame, text=_("label_back_sub_lang")).grid(column=0, row=4, sticky=tk.E, pady=2)  # 右对齐
        self.back_subtitle_combobox = ttk.Combobox(frame, width=40, state="readonly")
        ComboboxSearch(self.back_subtitle_combobox)
        self.back_subtitle_combobox.grid(column=1, row=4, sticky=(tk.W, tk.E), padx=5, pady=2)

        # 仅下载字幕
        self.download_only_subtitles_check = ttk.Checkbutton(frame, text=_("check_download_only_subs"), variable=self.download_only_subtitles_var)
        self.download_only_subtitles_check.grid(column=1, row=5, sticky=tk.W, pady=2)

        # 下载按钮
        self.download_button = ttk.Button(frame, text=_("button_start_download"), command=self.start_download)
        self.download_button.grid(column=1, row=6, sticky=tk.E, pady=10)
        self.download_button["state"] = "disabled"  # 初始状态禁用，直到查询完成

        # 让第二列自动扩展
        frame.columnconfigure(1, weight=1)
    
    def _update_dont_validate_url_config(self):
        self.config["dont_validate_url"] = self.dont_validate_url_var.get()
        self.logger.info(_("log_url_validation_changed", "enabled" if not self.config["dont_validate_url"] else "disabled"))

    def setup_csv_tab(self):
        # 生成csv包选项卡内容
        # Clear existing widgets
        for widget in self.csv_tab.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.csv_tab, padding="5")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用辅助函数创建输入行
        self.csv_file_entry = self._create_file_input_row(frame, _("label_csv_file"), 0, self.browse_csv_file)
        self.csv_output_dir_entry = self._create_file_input_row(frame, _("label_output_dir"), 1, self.browse_csv_output_dir, is_directory=True)

        # 新增：Anki包名称
        ttk.Label(frame, text=_("label_anki_package_name")).grid(column=0, row=2, sticky=tk.E, pady=2)
        self.csv_anki_package_name_entry = ttk.Entry(frame)
        self.csv_anki_package_name_entry.grid(column=1, row=2, sticky=(tk.W, tk.E), padx=5, pady=2)

        # TTS引擎选择
        ttk.Label(frame, text=_("label_tts_engine")).grid(column=0, row=3, sticky=tk.E, pady=2)
        self.csv_tts_engine_var = tk.StringVar(value=self.config.get("tts_engine", "gtts"))
        self.csv_tts_engine_frame = ttk.Frame(frame)
        self.csv_tts_engine_frame.grid(column=1, row=3, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Radiobutton(self.csv_tts_engine_frame, text="gTTS", variable=self.csv_tts_engine_var, value="gtts").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.csv_tts_engine_frame, text="edge-tts", variable=self.csv_tts_engine_var, value="edge-tts").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.csv_tts_engine_frame, text=_("radio_no_tts"), variable=self.csv_tts_engine_var, value="none").pack(side=tk.LEFT, padx=10)

        # 慢速语音选项 (仅gTTS)
        ttk.Label(frame, text=_("label_slow_speech")).grid(column=0, row=4, sticky=tk.E, pady=2)
        self.csv_slow_tts_frame = ttk.Frame(frame)
        self.csv_slow_tts_frame.grid(column=1, row=4, sticky=tk.W, pady=2)
        
        self.csv_slow_front_tts_var = tk.BooleanVar(value=False)
        self.csv_slow_front_tts_check = ttk.Checkbutton(self.csv_slow_tts_frame, text=_("check_slow_front"), variable=self.csv_slow_front_tts_var)
        self.csv_slow_front_tts_check.pack(side=tk.LEFT, padx=(0, 10))

        self.csv_slow_back_tts_var = tk.BooleanVar(value=False)
        self.csv_slow_back_tts_check = ttk.Checkbutton(self.csv_slow_tts_frame, text=_("check_slow_back"), variable=self.csv_slow_back_tts_var)
        self.csv_slow_back_tts_check.pack(side=tk.LEFT)

        # 新增：注音选项
        ttk.Label(frame, text=_("label_ruby_char_options")).grid(column=0, row=5, sticky=tk.E, pady=2)
        csv_ruby_frame = ttk.Frame(frame)
        csv_ruby_frame.grid(column=1, row=5, sticky=tk.W, pady=2)

        self.csv_add_ruby_front_var = tk.BooleanVar(value=True)
        self.csv_add_ruby_front_check = ttk.Checkbutton(csv_ruby_frame, text=_("check_add_ruby_front"), variable=self.csv_add_ruby_front_var)
        self.csv_add_ruby_front_check.pack(side=tk.LEFT, padx=(0, 10))

        self.csv_add_ruby_back_var = tk.BooleanVar(value=True)
        self.csv_add_ruby_back_check = ttk.Checkbutton(csv_ruby_frame, text=_("check_add_ruby_back"), variable=self.csv_add_ruby_back_var)
        self.csv_add_ruby_back_check.pack(side=tk.LEFT)

        # 新增：完成后清理中间文件
        ttk.Label(frame, text=_("label_post_processing")).grid(column=0, row=6, sticky=tk.E, pady=2)
        csv_cleanup_frame = ttk.Frame(frame)
        csv_cleanup_frame.grid(column=1, row=6, sticky=tk.W, pady=2)

        self.csv_cleanup_mp3_var = tk.BooleanVar(value=True)
        self.csv_cleanup_mp3_check = ttk.Checkbutton(csv_cleanup_frame, text=_("check_cleanup_mp3"), variable=self.csv_cleanup_mp3_var)
        self.csv_cleanup_mp3_check.pack(side=tk.LEFT, padx=(0, 10))

        self.csv_cleanup_preview_html_var = tk.BooleanVar(value=True)
        self.csv_cleanup_preview_html_check = ttk.Checkbutton(csv_cleanup_frame, text=_("check_cleanup_preview_html"), variable=self.csv_cleanup_preview_html_var)
        self.csv_cleanup_preview_html_check.pack(side=tk.LEFT, padx=(0, 10))

        # 新增：覆盖现有文件选项
        ttk.Label(frame, text=_("label_file_handling")).grid(column=0, row=7, sticky=tk.E, pady=2)
        csv_overwrite_frame = ttk.Frame(frame)
        csv_overwrite_frame.grid(column=1, row=7, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.csv_overwrite_apkg_var = tk.BooleanVar(value=True) # 默认选中
        self.csv_overwrite_apkg_check = ttk.Checkbutton(csv_overwrite_frame, text=_("check_overwrite_anki"), variable=self.csv_overwrite_apkg_var)
        self.csv_overwrite_apkg_check.pack(side=tk.LEFT, padx=(0, 10))

        # 生成按钮
        csv_button_frame = ttk.Frame(frame)
        csv_button_frame.grid(column=1, row=8, sticky=tk.E, pady=10)

         # 添加预览按钮
        self.csv_preview_button = ttk.Button(csv_button_frame, text=_("button_preview"), command=self.preview_anki_from_csv)
        self.csv_preview_button.pack(side=tk.LEFT, padx=5)


        self.csv_generate_button = ttk.Button(csv_button_frame, text=_("button_generate"), command=self.generate_anki_from_csv)
        self.csv_generate_button.pack(side=tk.LEFT, padx=5)

       
        # 让第二列自动扩展
        frame.columnconfigure(1, weight=1)

    def preview_anki_from_csv(self):
        csv_file = self.csv_file_entry.get()
        if not csv_file:
            self.logger.error(_("error_need_csv_file"))
            return

        anki_config = AnkiConfig()
        anki_config.output_dir = self.csv_output_dir_entry.get()
        anki_config.anki_package_name = self.csv_anki_package_name_entry.get()

        # 创建线程执行查询，避免界面卡顿
        threading.Thread(target=self._preview_anki_from_csv_thread, args=(csv_file, anki_config), daemon=True).start()

    def _preview_anki_from_csv_thread(self, csv_file, anki_config):
        try:
            self.logger.info(_("log_preview_generating"))

            cards_data = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # 跳过标题行
                for row in reader:
                    if len(row) >= 2:
                        cards_data.append({
                            'front_text': row[0],
                            'back_text': row[1]
                        })

            # 生成HTML预览
            html_content = self._build_preview_html(cards_data)

            # 保存预览文件
            preview_file = os.path.join(anki_config.output_dir, "anki_csv_preview.html")
            self.check_output_directory(anki_config.output_dir)
            
            with open(preview_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            # 打开浏览器查看预览
            webbrowser.open(f"file://{os.path.abspath(preview_file)}")

        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_generating_preview", e)))

    def browse_csv_file(self):
        file = filedialog.askopenfilename(filetypes=[(_("filetype_csv_files"), "*.csv")])
        if file:
            self.csv_file_entry.delete(0, tk.END)
            self.csv_file_entry.insert(0, file)

            # 新增：自动设置输出目录
            output_dir = os.path.join(os.path.dirname(file), "output")
            self.csv_output_dir_entry.delete(0, tk.END)
            self.csv_output_dir_entry.insert(0, output_dir)
            self.logger.info(_("log_auto_set_output_dir", output_dir))

            # 自动设置Anki包名称
            self.csv_anki_package_name_entry.delete(0, tk.END)
            self.csv_anki_package_name_entry.insert(0, os.path.splitext(os.path.basename(file))[0])
            self.logger.info(_("log_auto_set_package_name", os.path.splitext(os.path.basename(file))[0]))

    def browse_csv_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.csv_output_dir_entry.delete(0, tk.END)
            self.csv_output_dir_entry.insert(0, directory)

    def generate_anki_from_csv(self):
        csv_file = self.csv_file_entry.get()
        output_dir = self.csv_output_dir_entry.get()
        anki_package_name = self.csv_anki_package_name_entry.get()

        if not csv_file:
            self.logger.error(_("error_need_csv_file"))
            return
        
        if not output_dir:
            self.logger.error(_("error_need_output_dir"))
            return

        if not anki_package_name:
            self.logger.error(_("error_need_package_name"))
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.logger.info(_("log_created_download_dir", output_dir))
            except Exception as e:
                self.logger.error(_("error_creating_download_dir", e))
                return

        self.csv_generate_button["state"] = "disabled"

        anki_config= AnkiConfig()

        anki_config.anki_package_name=anki_package_name
        anki_config.csv_file=csv_file
        anki_config.output_dir=output_dir
        anki_config.source_type="csv"
        
        anki_config.add_ruby_front = self.csv_add_ruby_front_var.get()
        anki_config.add_ruby_back = self.csv_add_ruby_back_var.get()
        anki_config.slow_front = self.csv_slow_front_tts_var.get()
        anki_config.slow_back = self.csv_slow_back_tts_var.get()
        anki_config.cleanup_mp3 = self.csv_cleanup_mp3_var.get()
        anki_config.cleanup_preview_html = self.csv_cleanup_preview_html_var.get()
        anki_config.overwrite_apkg = self.csv_overwrite_apkg_var.get()
        anki_config.tts_engine=self.csv_tts_engine_var.get()

        anki_config.cleanup_csv=False
        anki_config.cleanup_jpg=False        
        anki_config.extract_audio_segment=False

        # 创建线程执行查询，避免界面卡顿
        threading.Thread(target=self._generate_anki_from_csv_thread, args=(anki_config,), daemon=True).start()
            
    def _generate_anki_from_csv_thread(self, anki_config):
        try:
            csv_file = anki_config.csv_file

            self.logger.info(_("log_anki_generating_from_csv"))
            self.logger.info(f"{_('label_csv_file')} {anki_config.csv_file}")
            self.logger.info(f"{_('label_output_dir')} {anki_config.output_dir}")

            # 从CSV读取数据
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                cards_data = []
                for row in reader:
                    if len(row) >= 2: # Ensure row has at least two columns for front and back text
                        cards_data.append({'front_text': row[0], 'back_text': row[1]})


            # 调用核心方法
            self._create_anki_package_core(cards_data, anki_config)

        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_generating_anki_pkg", e)))
        finally:
            self.root.after(0, lambda: self.csv_generate_button.configure(state="normal"))

    def _create_anki_package_core(self, cards_data, anki_config):
        """
        核心Anki包生成逻辑，处理卡片数据、TTS、注音、截图和打包。
        cards_data: 列表，每个元素是一个字典，包含 'front_text', 'back_text', 'start_ms', 'end_ms', 'media_file_path' 等。
                    对于CSV模式，'start_ms', 'end_ms', 'media_file_path' 可能为空。
        config: 字典，包含生成Anki包所需的所有配置参数。
        """

        media_files_to_cleanup = []
        screenshot_files_to_cleanup = []
        csv_file_to_cleanup = None # Only for subtitle mode

        try:
            self.root.after(0, lambda: self.progress_bar.configure(mode='determinate', value=0))
            
            output_apkg_path = os.path.join(anki_config.output_dir, f"{anki_config.anki_package_name}.apkg")
            if os.path.exists(output_apkg_path) and not anki_config.overwrite_apkg:
                self.root.after(0, lambda: self.logger.error(_("error_anki_pkg_exists", f"{anki_config.anki_package_name}.apkg")))
                return

            front_lang=self.config.get("preferred_front_language")
            back_lang=self.config.get("preferred_back_language")

            self.logger.info(_("log_detected_front_lang", front_lang))
            self.logger.info(_("log_detected_back_lang", back_lang))

            
            kks = None
            if 'ja' in [front_lang.lower(), back_lang.lower()]:
                try:
                    self.root.after(0, lambda: self.logger.info(_("log_ja_detected_init_kakasi")))
                    kks = pykakasi.kakasi()
                    self.root.after(0, lambda: self.logger.info(_("log_kakasi_initialized")))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.logger.error(_("error_init_kakasi", e)))

            is_front_chinese = 'zh-hans' in front_lang.lower() or 'zh-hant' in front_lang.lower()
            is_back_chinese = 'zh-hans' in back_lang.lower() or 'zh-hant' in back_lang.lower()
            if is_front_chinese or is_back_chinese:
                self.root.after(0, lambda: self.logger.info(_("log_zh_detected_add_pinyin")))

            is_front_korean = 'ko' in front_lang.lower()
            is_back_korean = 'ko' in back_lang.lower()
            if is_front_korean or is_back_korean:
                self.root.after(0, lambda: self.logger.info(_("log_ko_detected_add_romanization")))

            total_cards = len(cards_data)
            last_progress_update = -1
            
            deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), anki_config.anki_package_name)
            model = genanki.Model(
                random.randrange(1 << 30, 1 << 31),
                _("anki_model_name"),
                fields=[
                    {'name': 'Question'},
                    {'name': 'Answer'},
                    {'name': 'Audio_Question'},
                    {'name': 'Audio_Answer'},
                    {'name': 'Screenshot'}
                ],
                templates=[
                    {
                        'name': _("anki_card_name"),
                        'qfmt': self.config["anki_templates"]["front"],
                        'afmt': self.config["anki_templates"]["back"],
                    },
                ],
                css=self.config["anki_style"]
            )

            # Load media file if needed (only for subtitle mode)
            audio_segment = None
            if anki_config.source_type == "subtitle" and anki_config.media_file:
                try:
                    self.root.after(0, lambda: self.logger.info(_("log_loading_media_file", anki_config.media_file)))
                    audio_segment = AudioSegment.from_file(anki_config.media_file)
                    self.root.after(0, lambda: self.logger.info(_("log_media_file_loaded")))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.logger.error(_("error_loading_media_file", e)))
                    # If media file cannot be loaded, disable audio extraction and screenshot
                    anki_config["add_screenshot"] = False
                    # tts_engine = "none" # Force no TTS if audio segment fails

            for i, card_data in enumerate(cards_data):
                current_progress = (i / total_cards) * 100
                if current_progress - last_progress_update >= 1 or i == total_cards - 1:
                    self.root.after(0, lambda p=current_progress: self.progress_bar.configure(value=p))
                    self.root.after(0, lambda p=current_progress: self.logger.info(_("log_generation_progress", p)))
                    last_progress_update = current_progress

                front_text = card_data['front_text']
                back_text = card_data['back_text']
                
                # 保存原始文本以用于TTS
                front_text_for_tts = front_text
                back_text_for_tts = back_text

                if anki_config.add_ruby_front:
                    if kks and 'ja' in front_lang.lower():
                        front_text = add_furigana(kks, front_text)
                    elif is_front_chinese:
                        front_text = add_pinyin(front_text)
                    elif is_front_korean:
                        front_text = add_romanization_ko(front_text)
                
                if anki_config.add_ruby_back:
                    if kks and 'ja' in back_lang.lower():
                        back_text = add_furigana(kks, back_text)
                    elif is_back_chinese:
                        back_text = add_pinyin(back_text)
                    elif is_back_korean:
                        back_text = add_romanization_ko(back_text)

                if not front_text or not back_text:
                    continue
                
                audio_q_field = ""
                audio_a_field = ""
                screenshot_field = ""

                preffered_tts_engine=anki_config.tts_engine
 
                # Handle TTS audio
                if (preffered_tts_engine != 'none'):
                    front_audio = f"segment_front_{i+1:06d}.mp3"
                    back_audio = f"segment_back_{i+1:06d}.mp3"
                    
                    front_audio_path = os.path.join(anki_config.output_dir, front_audio)
                    back_audio_path = os.path.join(anki_config.output_dir, back_audio)
                    
                    if self._try_generate_audio_with_fallback(front_text_for_tts, preffered_tts_engine,front_audio_path, front_lang, slow=anki_config.slow_front):
                        media_files_to_cleanup.append(front_audio_path)
                        audio_q_field = f"[sound:{front_audio}]"
                    
                    if self._try_generate_audio_with_fallback(back_text_for_tts, preffered_tts_engine,back_audio_path, back_lang, slow=anki_config.slow_back):
                        media_files_to_cleanup.append(back_audio_path)
                        audio_a_field = f"[sound:{back_audio}]"
                
                # Handle audio segment extraction (only for subtitle mode)
                if anki_config.source_type == "subtitle" and audio_segment and anki_config.extract_audio_segment:
                    start_ms = card_data.get('start_ms')
                    end_ms = card_data.get('end_ms')
                    media_file_path = anki_config.media_file
                    timeline_offset_ms = anki_config.timeline_offset_ms

                    if start_ms is not None and end_ms is not None and media_file_path:
                        # Apply offset to start and end times
                        adjusted_start_ms = max(0, start_ms + timeline_offset_ms)
                        adjusted_end_ms = max(0, end_ms + timeline_offset_ms)

                        segment_audio_file = f"segment_media_{i+1:06d}.mp3"
                        segment_audio_path = os.path.join(anki_config.output_dir, segment_audio_file)
                        
                        if self.extract_audio_segment(audio_segment, adjusted_start_ms, adjusted_end_ms, segment_audio_path):
                            media_files_to_cleanup.append(segment_audio_path)
                            # Decide whether to use TTS audio or extracted audio for Question field
                            # For now, extracted audio takes precedence if available and requested
                            audio_q_field = f"[sound:{segment_audio_file}]"
                            # If you want both, you'd need to modify the Anki template or concatenate audio
                        else:
                            self.root.after(0, lambda: self.logger.warning(_("warning_audio_extraction_failed", i+1)))

                # Handle screenshot (only for subtitle mode)
                if anki_config.source_type == "subtitle" and anki_config.add_screenshot and anki_config.media_file:
                    screenshot_file = f"screenshot_{i+1:06d}.jpg"
                    screenshot_path = os.path.join(anki_config.output_dir, screenshot_file)
                    
                    timestamp_ms = None
                    if card_data.get('start_ms') is not None and card_data.get('end_ms') is not None:
                        start_ms = card_data['start_ms']
                        end_ms = card_data['end_ms']
                        
                        # Apply offset to timestamps
                        start_ms += anki_config.timeline_offset_ms
                        end_ms += anki_config.timeline_offset_ms

                        if anki_config.screenshot_time == _("screenshot_time_start"):
                            timestamp_ms = start_ms
                        elif anki_config.screenshot_time == _("screenshot_time_middle"):
                            timestamp_ms = (start_ms + end_ms) / 2
                        elif anki_config.screenshot_time == _("screenshot_time_end"):
                            timestamp_ms = end_ms
                    
                    if timestamp_ms is not None:
                        if self.take_screenshot(anki_config.media_file, timestamp_ms, screenshot_path, anki_config.screenshot_quality) and os.path.exists(screenshot_path):
                            screenshot_files_to_cleanup.append(screenshot_path)
                            screenshot_field = f"<img src=\"{screenshot_file}\">"
                        else:
                            self.root.after(0, lambda: self.logger.warning(_("warning_screenshot_failed", i+1)))
                    else:
                        self.root.after(0, lambda: self.logger.warning(_("warning_screenshot_no_timestamp", i+1)))

                note = genanki.Note(
                    model=model,
                    fields=[front_text, back_text, audio_q_field, audio_a_field, screenshot_field]
                )
                deck.add_note(note)
            
            package = genanki.Package(deck)
            package.media_files = media_files_to_cleanup + screenshot_files_to_cleanup # Add all media files to package
            
            output_file = os.path.join(anki_config.output_dir, f"{anki_config.anki_package_name}.apkg")
            package.write_to_file(output_file)
            
            self.root.after(0, lambda: self.progress_bar.configure(value=100))
            self.root.after(0, lambda: self.logger.info(_("log_anki_pkg_complete", output_file)))

        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_generating_anki_pkg", e)))
        finally:
            self.root.after(0, lambda: self._cleanup_temp_files(media_files_to_cleanup, csv_file_to_cleanup, screenshot_files_to_cleanup, anki_config))
    
    def setup_generate_tab(self):
        # 生成Anki包选项卡内容
        # Clear existing widgets
        for widget in self.anki_tab.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.anki_tab, padding="5")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用辅助函数创建输入行
        self.media_entry = self._create_file_input_row(frame, _("label_media_file"), 0, self.browse_media_file)
        self.front_subtitle_entry = self._create_file_input_row(frame, _("label_front_sub_file"), 1, lambda: self.browse_subtitle_file(self.front_subtitle_entry))
        self.back_subtitle_entry = self._create_file_input_row(frame, _("label_back_sub_file"), 2, lambda: self.browse_subtitle_file(self.back_subtitle_entry))
        self.output_dir_entry = self._create_file_input_row(frame, _("label_output_dir"), 3, self.browse_output_dir, is_directory=True)

        ToolTip(self.media_entry, _("tooltip_label_media_file"))

        # 新增：Anki包名称
        ttk.Label(frame, text=_("label_anki_package_name")).grid(column=0, row=4, sticky=tk.E, pady=2)
        self.anki_package_name_entry = ttk.Entry(frame)
        self.anki_package_name_entry.grid(column=1, row=4, sticky=(tk.W, tk.E), padx=5, pady=2)

        # 新增：截图选项
        ttk.Label(frame, text=_("label_screenshot_options")).grid(column=0, row=5, sticky=tk.E, pady=2)
        screenshot_options_frame = ttk.Frame(frame)
        screenshot_options_frame.grid(column=1, row=5, sticky=(tk.W, tk.E), padx=5, pady=2)

        self.add_screenshot_var = tk.BooleanVar(value=False)
        self.add_screenshot_check = ttk.Checkbutton(screenshot_options_frame, text=_("check_add_screenshot"), variable=self.add_screenshot_var)
        self.add_screenshot_check.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(screenshot_options_frame, text=_("label_screenshot_timestamp")).pack(side=tk.LEFT, padx=(0, 10))
        self.screenshot_time_var = tk.StringVar(value=_("screenshot_time_middle"))
        self.screenshot_time_combobox = ttk.Combobox(screenshot_options_frame, textvariable=self.screenshot_time_var, values=[_("screenshot_time_start"), _("screenshot_time_middle"), _("screenshot_time_end")], width=10, state="readonly")
        self.screenshot_time_combobox.pack(side=tk.LEFT, padx=(0, 10))
        ComboboxSearch(self.screenshot_time_combobox)

        ttk.Label(screenshot_options_frame, text=_("label_screenshot_quality")).pack(side=tk.LEFT, padx=(0, 10))
        self.screenshot_quality_spinbox = ttk.Spinbox(screenshot_options_frame, from_=1, to=31, increment=1, width=5)
        self.screenshot_quality_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        self.screenshot_quality_spinbox.set(2)

        # TTS引擎选择
        ttk.Label(frame, text=_("label_tts_engine")).grid(column=0, row=9, sticky=tk.E, pady=2)
        self.tts_engine_var = tk.StringVar(value=self.config.get("tts_engine", "gtts"))
        self.tts_engine_frame = ttk.Frame(frame)
        self.tts_engine_frame.grid(column=1, row=9, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Radiobutton(self.tts_engine_frame, text="gTTS", variable=self.tts_engine_var, value="gtts").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.tts_engine_frame, text="edge-tts", variable=self.tts_engine_var, value="edge-tts").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.tts_engine_frame, text=_("radio_no_tts"), variable=self.tts_engine_var, value="none").pack(side=tk.LEFT, padx=10)

        # 慢速语音选项 (仅gTTS)
        ttk.Label(frame, text=_("label_slow_speech")).grid(column=0, row=10, sticky=tk.E, pady=2)
        self.slow_tts_frame = ttk.Frame(frame)
        self.slow_tts_frame.grid(column=1, row=10, sticky=tk.W, pady=2)
        
        self.slow_front_tts_var = tk.BooleanVar(value=False)
        self.slow_front_tts_check = ttk.Checkbutton(self.slow_tts_frame, text=_("check_slow_front"), variable=self.slow_front_tts_var)
        self.slow_front_tts_check.pack(side=tk.LEFT, padx=(0, 10))

        self.slow_back_tts_var = tk.BooleanVar(value=False)
        self.slow_back_tts_check = ttk.Checkbutton(self.slow_tts_frame, text=_("check_slow_back"), variable=self.slow_back_tts_var)
        self.slow_back_tts_check.pack(side=tk.LEFT)

        # 新增：移除字幕中的非对话内容
        ttk.Label(frame, text=_("label_subtitle_cleanup")).grid(column=0, row=11, sticky=tk.E, pady=2)
        self.clean_subtitle_var = tk.BooleanVar(value=True)
        self.clean_subtitle_check = ttk.Checkbutton(frame, text=_("check_remove_non_dialogue"), variable=self.clean_subtitle_var)
        self.clean_subtitle_check.grid(column=1, row=11, sticky=tk.W, pady=2)

        # 新增：注音选项
        ttk.Label(frame, text=_("label_ruby_char_options")).grid(column=0, row=12, sticky=tk.E, pady=2)
        ruby_frame = ttk.Frame(frame)
        ruby_frame.grid(column=1, row=12, sticky=tk.W, pady=2)

        self.add_ruby_front_var = tk.BooleanVar(value=True)
        self.add_ruby_front_check = ttk.Checkbutton(ruby_frame, text=_("check_add_ruby_front"), variable=self.add_ruby_front_var)
        self.add_ruby_front_check.pack(side=tk.LEFT, padx=(0, 10))

        self.add_ruby_back_var = tk.BooleanVar(value=True)
        self.add_ruby_back_check = ttk.Checkbutton(ruby_frame, text=_("check_add_ruby_back"), variable=self.add_ruby_back_var)
        self.add_ruby_back_check.pack(side=tk.LEFT)

        # 新增：完成后清理中间文件
        ttk.Label(frame, text=_("label_post_processing")).grid(column=0, row=13, sticky=tk.E, pady=2)
        cleanup_frame = ttk.Frame(frame)
        cleanup_frame.grid(column=1, row=13, sticky=tk.W, pady=2)

        self.cleanup_mp3_var = tk.BooleanVar(value=True)
        self.cleanup_mp3_check = ttk.Checkbutton(cleanup_frame, text=_("check_cleanup_mp3"), variable=self.cleanup_mp3_var)
        self.cleanup_mp3_check.pack(side=tk.LEFT, padx=(0, 10))

        self.cleanup_csv_var = tk.BooleanVar(value=True)
        self.cleanup_csv_check = ttk.Checkbutton(cleanup_frame, text=_("check_cleanup_csv"), variable=self.cleanup_csv_var)
        self.cleanup_csv_check.pack(side=tk.LEFT)

        self.cleanup_jpg_var = tk.BooleanVar(value=True)
        self.cleanup_jpg_check = ttk.Checkbutton(cleanup_frame, text=_("check_cleanup_jpg"), variable=self.cleanup_jpg_var)
        self.cleanup_jpg_check.pack(side=tk.LEFT, padx=(0, 10))

        self.cleanup_preview_html_var = tk.BooleanVar(value=True)
        self.cleanup_preview_html_check = ttk.Checkbutton(cleanup_frame, text=_("check_cleanup_preview_html"), variable=self.cleanup_preview_html_var)
        self.cleanup_preview_html_check.pack(side=tk.LEFT, padx=(0, 10))

        # 新增：时间轴偏移
        ttk.Label(frame, text=_("label_timeline_offset")).grid(column=0, row=14, sticky=tk.E, pady=2)
        self.offset_spinbox = ttk.Spinbox(frame, from_=-30000, to=30000, increment=100, width=10)
        self.offset_spinbox.grid(column=1, row=14, sticky=tk.W, padx=5, pady=2)
        self.offset_spinbox.set(0)

        # 新增：字幕时间段选择
        ttk.Label(frame, text=_("label_subtitle_time_range")).grid(column=0, row=15, sticky=tk.E, pady=2)
        time_range_frame = ttk.Frame(frame)
        time_range_frame.grid(column=1, row=15, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(time_range_frame, text=_("label_start_time")).pack(side=tk.LEFT)
        self.start_time_entry = ttk.Entry(time_range_frame, width=12)
        self.start_time_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(time_range_frame, text=_("label_end_time")).pack(side=tk.LEFT)
        self.end_time_entry = ttk.Entry(time_range_frame, width=12)
        self.end_time_entry.pack(side=tk.LEFT)
        ttk.Label(time_range_frame, text=_("label_empty_for_end")).pack(side=tk.LEFT, padx=5)

        # 新增：字幕合并
        merge_label = ttk.Label(frame, text=_("label_subtitle_merge"), foreground="red")
        merge_label.grid(column=0, row=16, sticky=tk.E, pady=2)
        ToolTip(merge_label, _("tooltip_merge_warning"))

        merge_frame = ttk.Frame(frame)
        merge_frame.grid(column=1, row=16, sticky=(tk.W, tk.E), padx=5, pady=2)

        self.merge_subtitles_var = tk.BooleanVar(value=False)
        self.merge_subtitles_check = ttk.Checkbutton(merge_frame, text=_("check_merge_subtitles"), variable=self.merge_subtitles_var)
        self.merge_subtitles_check.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(merge_frame, text=_("label_max_merge_gap")).pack(side=tk.LEFT)
        self.merge_gap_spinbox = ttk.Spinbox(merge_frame, from_=0, to=5000, increment=50, width=8)
        self.merge_gap_spinbox.pack(side=tk.LEFT)
        self.merge_gap_spinbox.set(200)

        # 新增：覆盖现有文件选项
        ttk.Label(frame, text=_("label_file_handling")).grid(column=0, row=17, sticky=tk.E, pady=2)
        overwrite_frame = ttk.Frame(frame)
        overwrite_frame.grid(column=1, row=17, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.overwrite_apkg_var = tk.BooleanVar(value=True) # 默认选中
        self.overwrite_apkg_check = ttk.Checkbutton(overwrite_frame, text=_("check_overwrite_anki"), variable=self.overwrite_apkg_var)
        self.overwrite_apkg_check.pack(side=tk.LEFT, padx=(0, 10))

        # 生成按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=1, row=18, sticky=tk.E, pady=10)

        self.preview_button = ttk.Button(button_frame, text=_("button_preview"), command=self.preview_anki_cards)
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = ttk.Button(button_frame, text=_("button_generate"), command=self.generate_anki_package)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # 让第二列自动扩展
        frame.columnconfigure(1, weight=1)
    
    def setup_config_tab(self):
        # 配置选项卡内容
        # Clear existing widgets
        for widget in self.config_tab.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.config_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 默认字幕语言偏好 - 使用下拉框
        ttk.Label(frame, text=_("label_default_front_lang")).grid(column=0, row=0, sticky=tk.E, pady=2)  # 右对齐
        language_options =  [get_lang_display(code) for code in self.supported_languages]
        self.front_lang_entry = tk.StringVar(value=get_lang_display(self.config.get("preferred_front_language", "")) if self.config.get("preferred_front_language", "") else "")
        self.front_lang_combobox = ttk.Combobox(frame, width=40, textvariable=self.front_lang_entry, values=language_options, state="readonly")
        ComboboxSearch(self.front_lang_combobox)
        self.front_lang_combobox.grid(column=1, row=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(frame, text=_("label_default_back_lang")).grid(column=0, row=1, sticky=tk.E, pady=2)  # 右对齐
        self.back_lang_entry = tk.StringVar(value=get_lang_display(self.config.get("preferred_back_language", "")) if self.config.get("preferred_back_language", "") else "")
        self.back_lang_combobox = ttk.Combobox(frame, width=40, textvariable=self.back_lang_entry, values=language_options, state="readonly")
        ComboboxSearch(self.back_lang_combobox)
        self.back_lang_combobox.grid(column=1, row=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        # 创建Anki模板和样式的Tab控件
        ttk.Label(frame, text=_("label_anki_template_style")).grid(column=0, row=2, sticky=tk.E, pady=2)  # 右对齐
        self.template_tab_control = ttk.Notebook(frame)
        self.template_tab_control.grid(column=1, row=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        
        # 创建三个子Tab页
        self.front_template_tab = ttk.Frame(self.template_tab_control)
        self.back_template_tab = ttk.Frame(self.template_tab_control)
        self.style_tab = ttk.Frame(self.template_tab_control)
        self.template_tab_control.add(self.front_template_tab, text=_("tab_front_template"))
        self.template_tab_control.add(self.back_template_tab, text=_("tab_back_template"))
        self.template_tab_control.add(self.style_tab, text=_("tab_stylesheet"))
        self.preview_template_tab = ttk.Frame(self.template_tab_control)
        self.template_tab_control.add(self.preview_template_tab, text=_("tab_preview_html_template"))
        
        # 正面模板文本框
        self.front_template_text = scrolledtext.ScrolledText(self.front_template_tab, width=40, height=10)
        self.front_template_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.front_template_text.insert(tk.END, self.config["anki_templates"]["front"])
        
        # 背面模板文本框
        self.back_template_text = scrolledtext.ScrolledText(self.back_template_tab, width=40, height=10)
        self.back_template_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.back_template_text.insert(tk.END, self.config["anki_templates"]["back"])
        
        # 样式表文本框
        self.style_text = scrolledtext.ScrolledText(self.style_tab, width=40, height=10)
        self.style_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.style_text.insert(tk.END, self.config["anki_style"])

        # 预览HTML模板文本框
        self.preview_html_template_text = scrolledtext.ScrolledText(self.preview_template_tab, width=40, height=10)
        self.preview_html_template_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.preview_html_template_text.insert(tk.END, self.config["preview_html_template"])
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=1, row=3, sticky=tk.E, pady=10)  # 右对齐
        self.restore_config_button = ttk.Button(button_frame, text=_("button_restore_config"), command=self.restore_config)
        self.restore_config_button.pack(side=tk.LEFT, padx=5)
        self.save_config_button = ttk.Button(button_frame, text=_("button_save_config"), command=self.save_config)
        self.save_config_button.pack(side=tk.LEFT, padx=5)

        # 让第二列自动扩展
        frame.columnconfigure(1, weight=1)
    
    def on_tab_changed(self, event):
        # 当选项卡切换时调用
        current_tab = self.tab_control.select()
        tab_index = self.tab_control.index(current_tab)
        if tab_index == 3:  # 配置Tab
            # 当切换到配置Tab时，确保显示最新配置
            self.update_config_tab()
    
    def update_config_tab(self):
        # 更新配置Tab页上的内容
        self.front_lang_entry.set(get_lang_display(self.config.get("preferred_front_language", "")) if self.config.get("preferred_front_language", "") else "")
        self.back_lang_entry.set(get_lang_display(self.config.get("preferred_back_language", "")) if self.config.get("preferred_back_language", "") else "")
        
        self.front_template_text.delete("1.0", tk.END)
        self.front_template_text.insert(tk.END, self.config["anki_templates"]["front"])
        
        self.back_template_text.delete("1.0", tk.END)
        self.back_template_text.insert(tk.END, self.config["anki_templates"]["back"])
        
        self.style_text.delete("1.0", tk.END)
        self.style_text.insert(tk.END, self.config["anki_style"])

        self.preview_html_template_text.delete("1.0", tk.END)
        self.preview_html_template_text.insert(tk.END, self.config["preview_html_template"])
        
        self.logger.info(_("log_config_updated"))


    def restore_config(self):
        # 重新加载配置并更新界面
        self.load_config()
        self.update_config_tab()
        self.logger.info(_("log_config_restored"))
    
    def save_config(self):
        # 从UI更新配置
        self.config["download_directory"] = self.download_dir_entry.get()
        # 保存时需要把友好名称还原为代码
        def extract_lang_code(display_name):
            for code, name in get_available_display_languages().items():
                if name in display_name:
                    return code
            # fallback: 提取括号内的代码
            match = re.search(r'\(([\w-]+)\)', display_name)
            return match.group(1) if match else display_name

        front_lang_code = extract_lang_code(self.front_lang_entry.get())
        back_lang_code = extract_lang_code(self.back_lang_entry.get())

        if front_lang_code == back_lang_code:
            messagebox.showwarning(_("app_title"), _("warning_same_subtitle_language"))
            # Find an alternative language for back_lang_code
            alternative_back_lang_code = None
            for code in self.supported_languages:
                if code != front_lang_code:
                    alternative_back_lang_code = code
                    break
            
            if alternative_back_lang_code:
                back_lang_code = alternative_back_lang_code
                self.back_lang_entry.set(get_lang_display(back_lang_code))
            else:
                messagebox.showerror(_("app_title"), _("error_no_alternative_language"))
                return # Stop saving if no alternative is found

        self.config["preferred_front_language"] = front_lang_code
        self.config["preferred_back_language"] = back_lang_code
        self.config["anki_templates"]["front"] = self.front_template_text.get("1.0", tk.END).strip()
        self.config["anki_templates"]["back"] = self.back_template_text.get("1.0", tk.END).strip()
        self.config["anki_style"] = self.style_text.get("1.0", tk.END).strip()
        self.config["tts_engine"] = self.tts_engine_var.get()
        self.config["preview_html_template"] = self.preview_html_template_text.get("1.0", tk.END).strip()
        self.config["dont_validate_url"] = self.dont_validate_url_var.get()
        
        # 保存到文件
        config_path = "config.json"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            self.logger.info(_("log_config_saved"))
        except Exception as e:
            self.logger.error(_("error_saving_config", e))
    
    def check_clipboard(self):
        # 检查剪贴板是否有符合条件的链接
        try:
            clipboard_text = pyperclip.paste()
            if self.is_valid_url(clipboard_text) and not self.url_entry.get():
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_text)
                self.logger.info(_("log_url_from_clipboard", clipboard_text))
        except Exception as e:
            self.logger.error(_("error_checking_clipboard", e))
    
    def is_valid_url(self, url):
        """
        检查URL是否为有效的YouTube单个视频URL。
        会拒绝播放列表URL。
        """
        if self.config.get("dont_validate_url", False):
            return True
        try:
            parsed_url = urlparse(url)
            
            # 检查有效的YouTube域名和单个视频的路径
            is_youtube_domain = parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']
            is_youtube_short_domain = parsed_url.hostname == 'youtu.be'

            if (is_youtube_domain and parsed_url.path == '/watch' and 'v=' in parsed_url.query) or \
               (is_youtube_short_domain and parsed_url.path):
                return True
        except (ValueError, AttributeError): # 捕获可能的解析错误
            return False
        return False
    
    def auto_fill_subtitle_files(self, media_file_path):
        """根据媒体文件路径，自动查找并填充字幕文件"""
        self.logger.info(_("log_trying_auto_match_subs", media_file_path))

        front_lang = self.config.get("preferred_front_language")
        back_lang = self.config.get("preferred_back_language")

        if not front_lang and not back_lang:
            self.logger.info(_("log_no_default_lang_for_match"))
            return

        directory = os.path.dirname(media_file_path)
        base_name = os.path.splitext(os.path.basename(media_file_path))[0]
        subtitle_extensions = ['.srt', '.vtt']

        def find_subtitle(lang_code):
            if not lang_code:
                return None
            try:
                files_in_dir = os.listdir(directory)
            except FileNotFoundError:
                return None

            potential_files = []
            for f in files_in_dir:
                if not f.lower().startswith(base_name.lower() + '.'):
                    continue
                if not any(f.lower().endswith(ext) for ext in subtitle_extensions):
                    continue

                file_base_name = os.path.splitext(f)[0]
                lang_part = file_base_name[len(base_name) + 1:]

                # 优先完全匹配
                if lang_part.lower() == lang_code.lower():
                    potential_files.append((f, 0))  # 优先级0
                # 其次前缀匹配
                elif lang_part.lower().startswith(lang_code.lower()):
                    potential_files.append((f, 1))  # 优先级1

            if not potential_files:
                return None

            potential_files.sort(key=lambda x: x[1])
            return os.path.join(directory, potential_files[0][0])

        # 查找并填充正面字幕
        if front_lang and (front_subtitle_file := find_subtitle(front_lang)):
            self.front_subtitle_entry.delete(0, tk.END)
            self.front_subtitle_entry.insert(0, front_subtitle_file)
            self.logger.info(_("log_auto_matched_front_sub", front_lang, front_subtitle_file))
            # 自动设置Anki包名称
            anki_package_name = os.path.splitext(os.path.basename(front_subtitle_file))[0]
            self.anki_package_name_entry.delete(0, tk.END)
            self.anki_package_name_entry.insert(0, anki_package_name)
            self.logger.info(_("log_auto_set_package_name", anki_package_name))

        # 查找并填充背面字幕
        if back_lang and (back_subtitle_file := find_subtitle(back_lang)):
            self.back_subtitle_entry.delete(0, tk.END)
            self.back_subtitle_entry.insert(0, back_subtitle_file)
            self.logger.info(_("log_auto_matched_back_sub", back_lang, back_subtitle_file))
    
    def _create_file_input_row(self, parent, label_text, row, command, is_directory=False):
        # 辅助函数，用于创建 Label, Entry, 和 Button 的组合控件
        ttk.Label(parent, text=label_text).grid(column=0, row=row, sticky=tk.E, pady=2)
        frame = ttk.Frame(parent)
        frame.grid(column=1, row=row, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        entry = ttk.Entry(frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        button = ttk.Button(frame, text=_("button_browse"), command=command)
        button.pack(side=tk.RIGHT, padx=5)
        
        return entry

    def query_video_info(self):
        # 查询视频信息
        url = self.url_entry.get()
        if not url:
            self.logger.error(_("error_enter_video_url"))
            return
        
        if not self.is_valid_url(url):
            self.logger.error(_("error_enter_valid_url"))
            return
        
        # 禁用查询按钮，防止重复点击
        self.query_button["state"] = "disabled"
        self.logger.info(_("log_querying_video_info", url))
        
        # 创建线程执行查询，避免界面卡顿
        threading.Thread(target=self._query_video_info_thread, args=(url,), daemon=True).start()
    
    def _query_video_info_thread(self, url):
        try:
            # 设置进度条为不确定模式
            self.root.after(0, lambda: self.progress_bar.configure(mode='indeterminate'))
            self.root.after(0, self.progress_bar.start)
            
            # 使用yt-dlp获取视频信息
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'listformats': True,
                'listsubtitles': True,
                'noplaylist': True,
                'writeautomaticsub': True, # Enable automatic subtitle generation
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 检查是否为播放列表
                if info.get('_type') == 'playlist':
                    self.root.after(0, lambda: self.logger.error(_("error_playlist_not_supported")))
                    self.root.after(0, lambda: messagebox.showerror(_("app_title"), _("error_playlist_not_supported")))
                    # 清理UI并返回，停止处理
                    return

                # 获取可用格式
                formats = []
                if 'formats' in info:
                    for f in info['formats']:
                        format_id = f.get('format_id', '')
                        format_note = f.get('format_note', '')
                        ext = f.get('ext', '')
                        if ext in ['mp3', 'mp4', 'webm', 'm4a']:
                            resolution = f.get('resolution', '')
                            format_desc = f"{format_id} - {format_note} ({ext}) {resolution}".strip()
                            formats.append((format_id, format_desc))
                                        
                # 获取可用字幕
                subtitles = []
                if 'subtitles' in info:
                    for lang, subs in info['subtitles'].items():
                        # 如果语言代码是 'zh'，则将其视为 'zh-Hans'
                        if lang.lower() == 'zh':
                            lang = 'zh-Hans'
                        lang_name = lang
                        for sub in subs:
                            sub_format = sub.get('ext', '')
                            # 仅保留 srt 和 vtt 格式的字幕
                            if sub_format in ['srt', 'vtt']:
                                subtitles.append((lang, f"{lang_name} ({sub_format})"))
                
                # 如果没有常规字幕，则添加自动生成的字幕
                if not subtitles and 'automatic_captions' in info:
                    for lang, subs in info['automatic_captions'].items():
                        # 如果语言代码是 'zh'，则将其视为 'zh-Hans'
                        if lang.lower() == 'zh':
                            lang = 'zh-Hans'
                        lang_name = lang
                        for sub in subs:
                            sub_format = sub.get('ext', '')
                            if sub_format in ['srt', 'vtt']:
                                subtitles.append((lang, f"{lang_name} (auto) ({sub_format})"))
                
                # 更新UI
                self.root.after(0, lambda: self._update_ui_after_query(formats, subtitles))
        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_querying_video_info", e)))
        finally:
            # 恢复进度条和按钮状态
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.progress_bar.configure(mode='determinate'))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            self.root.after(0, lambda: self.query_button.configure(state="normal"))
    
    def _update_ui_after_query(self, formats, subtitles):
        self.available_formats = formats
        self.available_subtitles = subtitles

        # 更新格式下拉框
        format_descs = [desc for _, desc in formats]
        self.format_combobox['values'] = format_descs
        if formats:
            # 查找最佳格式
            best_format_index = -1
            
            # 优先查找包含 "original" 和 "m4a" 的项
            for i, desc in enumerate(format_descs):
                desc_lower = desc.lower()
                if "original" in desc_lower and "m4a" in desc_lower:
                    best_format_index = i
                    break
            
            # 如果没找到，则查找包含 "m4a" 的项
            if best_format_index == -1:
                for i, desc in enumerate(format_descs):
                    if "m4a" in desc.lower():
                        best_format_index = i
                        break
            
            # 如果找到了最佳格式，则选中它，否则选中第一个
            if best_format_index != -1:
                self.format_combobox.current(best_format_index)
            else:
                self.format_combobox.current(0)

        # 更新字幕下拉框，使用国际化显示
        subtitle_values = [
            get_lang_display(lang) + f" [{desc.split('(')[-1].rstrip(')')}]" for lang, desc in subtitles
        ]
        self.front_subtitle_combobox['values'] = subtitle_values
        self.back_subtitle_combobox['values'] = subtitle_values

        # 如果有字幕，默认选择第一个
        if subtitles:
            self.front_subtitle_combobox.current(0)
            self.back_subtitle_combobox.current(0)

        # 根据偏好语言尝试找到更好的匹配
        preferred_front = self.config.get("preferred_front_language", "")
        preferred_back = self.config.get("preferred_back_language", "")
        
        if preferred_front:
            front_match_index = self._find_best_subtitle_match(preferred_front, subtitles)
            if front_match_index is not None:
                self.front_subtitle_combobox.current(front_match_index)

        if preferred_back:
            back_match_index = self._find_best_subtitle_match(preferred_back, subtitles)
            if back_match_index is not None:
                self.back_subtitle_combobox.current(back_match_index)

        # 启用下载按钮
        self.download_button["state"] = "normal"
        
        self.logger.info(_("log_query_complete", len(formats), len(subtitles)))
    
    def _find_best_subtitle_match(self, preferred_lang, available_subtitles):
        """查找最佳字幕匹配项，优先完全匹配，其次是前缀匹配，优先SRT格式。"""
        best_match_index = None
        best_match_priority = 999 # 0 for exact, 1 for prefix, 2 for auto, 3 for other
        
        for i, (lang_code, desc) in enumerate(available_subtitles):
            current_priority = 999
            is_auto = "(auto)" in desc.lower()
            is_srt = "(srt)" in desc.lower()

            # 优先完全匹配语言代码
            if lang_code.lower() == preferred_lang.lower():
                current_priority = 0
            # 其次是前缀匹配 (例如 'en' 匹配 'en-US')
            elif lang_code.lower().startswith(preferred_lang.lower()):
                current_priority = 1
            # 再次是自动字幕
            elif is_auto:
                current_priority = 2
            # 最后是其他字幕
            else:
                current_priority = 3

            # 如果优先级相同，优先选择 SRT 格式
            if current_priority < best_match_priority or \
               (current_priority == best_match_priority and is_srt and not ("(srt)" in available_subtitles[best_match_index][1].lower() if best_match_index is not None else False)):
                best_match_priority = current_priority
                best_match_index = i
        
        return best_match_index
        
    def browse_download_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_dir_entry.delete(0, tk.END)
            self.download_dir_entry.insert(0, directory)
    
    def browse_media_file(self):
        file = filedialog.askopenfilename(filetypes=[(_("filetype_media_files"), "*.mp4 *.webm *.m4a *.mp3 *.avi *.mkv")])
        if file:
            self.media_entry.delete(0, tk.END)
            self.media_entry.insert(0, file)

            # 新增：自动设置输出目录
            output_dir = os.path.join(os.path.dirname(file), "output")
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, output_dir)
            self.logger.info(_("log_auto_set_output_dir", output_dir))

            # 自动设置Anki包名称
            self.anki_package_name_entry.delete(0, tk.END)
            self.anki_package_name_entry.insert(0, os.path.splitext(os.path.basename(file))[0])
            self.logger.info(_("log_auto_set_package_name", os.path.splitext(os.path.basename(file))[0]))

            self.auto_fill_subtitle_files(file)
    
    def browse_subtitle_file(self, entry_widget):
        file = filedialog.askopenfilename(filetypes=[(_("filetype_subtitle_files"), "*.srt *.vtt")])
        if file:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file)

            # 新增：如果没有媒体文件，则根据字幕文件自动设置输出目录
            if not self.media_entry.get():
                output_dir = os.path.join(os.path.dirname(file), "output")
                self.output_dir_entry.delete(0, tk.END)
                self.output_dir_entry.insert(0, output_dir)
                self.logger.info(_("log_auto_set_output_dir_from_sub", output_dir))
            
            # 自动设置Anki包名称
            self.anki_package_name_entry.delete(0, tk.END)
            self.anki_package_name_entry.insert(0, os.path.splitext(os.path.basename(file))[0])
            self.logger.info(_("log_auto_set_package_name", os.path.splitext(os.path.basename(file))[0]))
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)
       
    def start_download(self):
        url = self.url_entry.get()
        download_dir = self.download_dir_entry.get()
        
        if not url:
            self.logger.error(_("error_enter_video_url"))
            return
        
        if not download_dir:
            self.logger.error(_("error_select_download_dir"))
            return
        
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
                self.logger.info(_("log_created_download_dir", download_dir))
            except Exception as e:
                self.logger.error(_("error_creating_download_dir", e))
                return
        
        # 获取选择的格式和字幕
        format_index = self.format_combobox.current()
        front_subtitle_index = self.front_subtitle_combobox.current()
        back_subtitle_index = self.back_subtitle_combobox.current()
        
        if format_index == -1:
            self.logger.error(_("error_select_av_format"))
            return
        
        if front_subtitle_index == -1 or back_subtitle_index == -1:
            self.logger.error(_("error_select_sub_lang"))
            return
        
        format_id = self.available_formats[format_index][0]
        front_subtitle_lang = self.available_subtitles[front_subtitle_index][0]
        back_subtitle_lang = self.available_subtitles[back_subtitle_index][0]
        download_only_subtitles = self.download_only_subtitles_var.get()
        
        # 禁用下载按钮，防止重复点击
        self.download_button["state"] = "disabled"
        
        # 创建线程执行下载，避免界面卡顿
        threading.Thread(
            target=self._download_thread, 
            args=(url, download_dir, format_id, front_subtitle_lang, back_subtitle_lang, download_only_subtitles),
            daemon=True
        ).start()
    
    def _download_thread(self, url, download_dir, format_id, front_subtitle_lang, back_subtitle_lang, download_only_subtitles):
        try:
            self.logger.info(_("log_processing_started", url))
            self.logger.info(_("log_download_dir", download_dir))
            self.logger.info(_("log_front_sub_lang", front_subtitle_lang))
            self.logger.info(_("log_back_sub_lang", back_subtitle_lang))
            
            # 重置进度条
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            
            # 构建yt-dlp选项
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(download_dir, "%(title)s.%(ext)s"),
                'writesubtitles': True,
                'writeautomaticsub': True, # Enable automatic subtitle download
                'subtitleslangs': list(set([front_subtitle_lang, back_subtitle_lang])), # 下载所有需要的字幕
                'subtitlesformat': 'srt',
                'progress_hooks': [self._download_progress_hook],
                'noplaylist': True, # 确保只下载单个视频
            }

            if download_only_subtitles:
                ydl_opts['skip_download'] = True
                self.logger.info(_("log_skip_media_download"))
            else:
                self.logger.info(_("log_selected_format", format_id))
                self.logger.info(_("log_starting_media_download"))

            media_file = None
            downloaded_files = []

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # yt-dlp 2023.07.06 之后，extract_info 返回的 info 字典中包含了 downloaded_filenames
                # 这是一个列表，包含所有下载的文件路径
                downloaded_files = info.get('requested_downloads', [])
                if not downloaded_files: # 兼容旧版本或某些特殊情况
                    # 尝试从 info 中获取文件名，这可能不包含所有下载的文件
                    # 尤其是当 skip_download=True 时，info['filepath'] 可能不存在
                    if 'filepath' in info and not download_only_subtitles:
                        downloaded_files.append(info['filepath'])
                    # 对于字幕，yt-dlp 不会直接在 info['filepath'] 中列出，需要通过 glob 查找

            # 查找实际下载的媒体文件
            if not download_only_subtitles:
                # 尝试从 downloaded_files 中找到媒体文件
                for f in downloaded_files:
                    if not f.get("filename").endswith(('.srt', '.vtt')):
                        media_file = f.get("filename")
                        break
                
                # 如果没有从 downloaded_files 中找到，则尝试根据 outtmpl 模式查找
                if not media_file:
                    # 假设媒体文件扩展名与 format_id 对应，或者从 info 中获取
                    # 这是一个更健壮的方法，但需要知道确切的扩展名
                    # 暂时先用 glob 查找，后续可以优化
                    base_name_pattern = os.path.join(download_dir, re.escape(info['title']) + '.*')
                    potential_media_files = glob.glob(base_name_pattern)
                    for f in potential_media_files:
                        if not f.endswith(('.srt', '.vtt')):
                            media_file = f
                            break
                
                if media_file:
                    self.logger.info(_("log_media_download_complete", media_file))
                else:
                    self.logger.warning(_("warning_media_file_not_found"))
            else:
                self.logger.info(_("log_skipped_media_download"))

            # 查找实际下载的字幕文件
            sanitized_title = re.escape(info['title'])
            front_subtitle_file = None
            back_subtitle_file = None

            # 查找正面字幕
            front_subtitle_pattern = os.path.join(download_dir, f"{sanitized_title}.{front_subtitle_lang}*.srt")
            front_subtitle_candidates = glob.glob(front_subtitle_pattern)
            if front_subtitle_candidates:
                front_subtitle_file = front_subtitle_candidates[0] # 取第一个匹配项
                self.logger.info(_("log_front_sub_download_complete", front_subtitle_file))
            else:
                self.logger.warning(_("warning_front_sub_not_found", front_subtitle_lang))

            # 查找背面字幕
            if back_subtitle_lang != front_subtitle_lang:
                back_subtitle_pattern = os.path.join(download_dir, f"{sanitized_title}.{back_subtitle_lang}*.srt")
                back_subtitle_candidates = glob.glob(back_subtitle_pattern)
                if back_subtitle_candidates:
                    back_subtitle_file = back_subtitle_candidates[0] # 取第一个匹配项
                    self.logger.info(_("log_back_sub_download_complete", back_subtitle_file))
                else:
                    self.logger.warning(_("warning_back_sub_not_found", back_subtitle_lang))
            else:
                back_subtitle_file = front_subtitle_file # 如果语言相同，则使用同一个文件

            # 保存下载结果
            self.download_results = {
                'media_file': media_file,
                'front_subtitle_file': front_subtitle_file,
                'back_subtitle_file': back_subtitle_file
            }
            
            # 更新UI
            self.root.after(0, lambda: self.progress_bar.configure(value=100))
            self.root.after(0, lambda: self.logger.info(_("log_download_complete_log")))
            self.root.after(0, self.ask_auto_fill())

        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_downloading", e)))
        finally:
            # 恢复下载按钮状态
            self.root.after(0, lambda: self.download_button.configure(state="normal"))

    def _download_progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total_bytes > 0:
                percent = d.get('downloaded_bytes', 0) / total_bytes * 100
                self.root.after(0, lambda: self.progress_bar.configure(value=percent))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.logger.info(_("log_download_finished_processing")))
    
    def ask_auto_fill(self):
        # 询问是否自动填充到生成Anki包页面
        if messagebox.askyesno(_("title_download_complete"), _("prompt_autofill")):
            # 填充媒体文件
            if 'media_file' in self.download_results and self.download_results['media_file']:
                self.media_entry.delete(0, tk.END)
                self.media_entry.insert(0, self.download_results['media_file'])

            # 优先根据默认语言自动查找字幕文件
            media_file = self.download_results.get('media_file')
            front_lang = self.config.get("preferred_front_language")
            back_lang = self.config.get("preferred_back_language")
            if media_file and (front_lang or back_lang):
                self.auto_fill_subtitle_files(media_file)
            else:
                # 如果没有媒体文件或没有配置默认语言，则回退为下载结果
                if 'front_subtitle_file' in self.download_results and self.download_results['front_subtitle_file']:
                    self.front_subtitle_entry.delete(0, tk.END)
                    self.front_subtitle_entry.insert(0, self.download_results['front_subtitle_file'])
                if 'back_subtitle_file' in self.download_results and self.download_results['back_subtitle_file']:
                    self.back_subtitle_entry.delete(0, tk.END)
                    self.back_subtitle_entry.insert(0, self.download_results['back_subtitle_file'])

            # 设置输出目录为下载目录下的 "output" 子目录
            download_dir = self.download_dir_entry.get()
            if download_dir:
                output_dir = os.path.join(download_dir, "output")
                self.output_dir_entry.delete(0, tk.END)
                self.output_dir_entry.insert(0, output_dir)
                self.logger.info(_("log_auto_set_output_dir", output_dir))

            # 自动设置Anki包名称为正面字幕文件名
            front_subtitle_file = self.front_subtitle_entry.get()
            if front_subtitle_file:
                front_subtitle_filename = os.path.basename(front_subtitle_file)
                anki_package_name = os.path.splitext(front_subtitle_filename)[0]
                self.anki_package_name_entry.delete(0, tk.END)
                self.anki_package_name_entry.insert(0, anki_package_name)
                self.logger.info(_("log_auto_set_package_name", anki_package_name))

            # 切换到生成Anki包页面
            self.tab_control.select(1)
    
    def detect_language_from_filename(self, filename):
        # 从文件名中检测语言代码
        try:
            # 尝试从文件名中提取语言代码
            match = re.search(r'[.-]([a-z]{2})[.-]', os.path.basename(filename))
            if match:
                lang_code = match.group(1)
                return lang_code
            
            # 如果没有找到，尝试从文件路径中提取
            for lang_code in self.supported_languages:
                if lang_code in filename.lower():
                    return lang_code
            
            # 默认返回英语
            return "en"
        except Exception as e:
            self.logger.error(_("error_detecting_lang", e))
            return "en"

    def get_voice_for_language(self, lang_code):
        # 获取语言对应的语音
        edge_tts_voices = {
            "en": "en-US-ChristopherNeural",
            "zh": "zh-CN-YunxiNeural",
            "ja": "ja-JP-KeitaNeural",
            "ko": "ko-KR-InJoonNeural",
            "fr": "fr-FR-HenriNeural",
            "de": "de-DE-ConradNeural",
            "es": "es-ES-AlvaroNeural",
            "it": "it-IT-DiegoNeural",
            "ru": "ru-RU-DmitryNeural",
            "pt": "pt-BR-AntonioNeural",    # 葡萄牙语 (巴西)
            "ar": "ar-SA-HamedNeural",      # 阿拉伯语 (沙特阿拉伯)
            "hi": "hi-IN-MadhurNeural",     # 印地语
            "id": "id-ID-ArdiNeural",       # 印度尼西亚语
            "tr": "tr-TR-AhmetNeural",      # 土耳其语
            "vi": "vi-VN-NamMinhNeural",    # 越南语
            "pl": "pl-PL-MarekNeural",      # 波兰语
            "nl": "nl-NL-MaartenNeural",    # 荷兰语
            "th": "th-TH-NiwatNeural",      # 泰语
            "sv": "sv-SE-MattiasNeural",    # 瑞典语
            "el": "el-GR-NestorasNeural",   # 希腊语
            "hu": "hu-HU-TamasNeural",      # 匈牙利语
            "cs": "cs-CZ-AntoninNeural",    # 捷克语
            "ro": "ro-RO-EmilNeural",       # 罗马尼亚语
            "fi": "fi-FI-HarriNeural",      # 芬兰语
            "da": "da-DK-JeppeNeural",      # 丹麦语
            "no": "nb-NO-FinnNeural",       # 挪威语
            # 添加更多语言映射
        }
        
        return edge_tts_voices.get(lang_code, "en-US-ChristopherNeural")
    
    def parse_srt_file(self, srt_file):
        # 解析SRT文件
        try:
            subs = pysrt.open(srt_file)
            return [(sub.start.ordinal, sub.end.ordinal, sub.text) for sub in subs]
        except Exception as e:
            self.logger.error(_("error_parsing_srt", e))
            return []

    def _parse_time_to_ms(self, time_str):
        """将 HH:MM:SS.sss, MM:SS.sss 或 SSS.sss 格式的时间字符串解析为毫秒"""
        if not time_str or not time_str.strip():
            return None
        
        # 移除所有空白字符并替换逗号为点
        time_str = time_str.strip().replace(',', '.').replace(' ', '')
        
        # 验证时间字符串格式
        if not re.match(r'^(\d+:)?(\d+:)?\d+(\.\d+)?$', time_str):
            # self.root.after(0, lambda: self.logger.error(_("error_invalid_time_format", time_str)))
            return None
        
        parts = time_str.split(':')
        try:
            if len(parts) > 3:
                raise ValueError("Invalid time format: too many colons")

            # 最后一部分是秒，可以是浮点数
            seconds = float(parts[-1])
            minutes = 0
            hours = 0

            # 分钟和小时部分必须是整数
            if len(parts) > 1:
                minutes = int(parts[-2])
            if len(parts) > 2:
                hours = int(parts[-3])

            # 验证时间组件范围
            if hours < 0 or minutes < 0 or seconds < 0:
                raise ValueError("Time components cannot be negative")
            if minutes >= 60:
                raise ValueError("Minutes must be less than 60")
            if seconds >= 60:
                raise ValueError("Seconds must be less than 60")

            total_seconds = hours * 3600 + minutes * 60 + seconds
            return int(total_seconds * 1000)

        except (ValueError, IndexError) as e:
            # self.root.after(0, lambda e=e: self.logger.error(_("error_invalid_time_format", f"{time_str} ({str(e)})")))
            return None

    def _filter_subtitles_by_time(self, subtitles, start_time_str, end_time_str):
        """根据时间字符串过滤字幕列表"""
        # 提前检查空输入
        if not subtitles:
            return []

        # 解析时间并记录日志（合并到单个日志调用）
        start_ms = self._parse_time_to_ms(start_time_str)
        end_ms = self._parse_time_to_ms(end_time_str)
        
        if start_ms is not None or end_ms is not None:
            log_msg = []
            if start_ms is not None:
                log_msg.append(_("log_applying_start_time", start_time_str, start_ms))
            if end_ms is not None:
                log_msg.append(_("log_applying_end_time", end_time_str, end_ms))
            # self.root.after(0, lambda: self.logger.info("; ".join(log_msg)))

        # 如果不需要过滤，直接返回原列表
        if start_ms is None and end_ms is None:
            return subtitles

        # 优化过滤逻辑：使用生成器表达式避免创建临时列表
        return list(
            s for s in subtitles 
            if (start_ms is None or s[0] >= start_ms) 
            and (end_ms is None or s[1] <= end_ms)
        )

    def _generate_tts_audio_engine(self, tts_engine, text, output_file, lang_code, slow=False):
        """使用指定的引擎生成TTS音频。"""
        try:
            if tts_engine == "gtts":
                gtts_lang = lang_code.split('-')[0]
                # gTTS 对中文的语言代码处理
                if gtts_lang == "zh":
                    if "zh-hans" in lang_code.lower():
                        gtts_lang = "zh-CN"
                    elif "zh-hant" in lang_code.lower():
                        gtts_lang = "zh-TW"
                    else:
                        gtts_lang = "zh-CN" # 默认简体中文
                
                tts = gTTS(text=text, lang=gtts_lang, slow=slow)
                tts.save(output_file)
                return True
            elif tts_engine == "edge-tts":
                if slow:
                    self.root.after(0, lambda: self.logger.warning(_("warning_edge_tts_no_slow")))
                voice = self.get_voice_for_language(lang_code)

                async def _generate_audio():
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(output_file)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(_generate_audio())
                loop.close()
                return True
            else:
                self.root.after(0, lambda: self.logger.error(_("error_unknown_tts_engine", tts_engine)))
                return False
        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_generating_tts", tts_engine, e)))
            return False

    def _try_generate_audio_with_fallback(self, text,preferred_engine, output_path, lang_code, slow):
        """
        尝试使用首选引擎生成TTS音频，如果失败则使用备用引擎。
        成功返回 True，失败返回 False。
        """
        
        fallback_engine = "edge-tts" if preferred_engine == "gtts" else "gtts"

        # 尝试首选引擎
        if self._generate_tts_audio_engine(preferred_engine, text, output_path, lang_code, slow):
            return True

        # 如果首选引擎失败，尝试备用引擎
        self.root.after(0, lambda: self.logger.warning(_("warning_tts_fallback", preferred_engine, fallback_engine)))
        if self._generate_tts_audio_engine(fallback_engine, text, output_path, lang_code, slow):
            self.root.after(0, lambda: self.logger.info(_("log_tts_fallback_success", fallback_engine)))
            return True

        return False # 如果两个引擎都失败，返回 False

    def generate_tts_audio(self, text, preferred_engine,output_file, lang_code, slow=False):
        """
        统一的TTS音频生成接口，使用 _try_generate_audio_with_fallback。
        """
        return self._try_generate_audio_with_fallback(text, preferred_engine,output_file, lang_code, slow)

    def _merge_subtitles(self, subtitles, max_gap_ms):
        """合并时间接近的字幕行"""
        if not subtitles or max_gap_ms <= 0:
            return subtitles

        merged_subtitles = []
        current_merge = None

        for sub in subtitles:
            start, end, text = sub
            if current_merge is None:
                current_merge = [start, end, text]
            else:
                # 如果当前字幕的开始时间与前一个合并字幕的结束时间之间的间隔小于等于最大间隔
                if start - current_merge[1] <= max_gap_ms:
                    current_merge[1] = end  # 更新结束时间
                    current_merge[2] += " " + text  # 合并文本
                else:
                    merged_subtitles.append(tuple(current_merge))
                    current_merge = [start, end, text]
        
        if current_merge is not None:
            merged_subtitles.append(tuple(current_merge))
            
        return merged_subtitles

    def extract_audio_segment(self, audio_segment, start_ms, end_ms, output_file):
        # 从已加载的音频数据中提取片段
        try:
            # 提取片段
            segment = audio_segment[start_ms:end_ms]
            
            # 保存片段
            segment.export(output_file, format="mp3")
            return True
        except Exception as e:
            self.logger.error(_("error_extracting_audio", e))
            return False
    
    def take_screenshot(self, video_file, timestamp_ms, output_file, quality=2):
        """使用ffmpeg在指定时间戳截图"""
        try:
            # 将毫秒转换为 HH:MM:SS.mmm 格式
            timestamp_sec = timestamp_ms / 1000
            # -y: 覆盖输出文件
            # -ss: 跳转到指定时间
            # -i: 输入文件
            # -vframes 1: 只截取一帧
            # -q:v: 设置图像质量 (1-31, 越低越好)
            command = [
                'ffmpeg',
                '-y',
                '-ss', str(timestamp_sec),
                '-i', video_file,
                '-vframes', '1',
                '-q:v', str(quality),
                output_file
            ]
            # 使用 subprocess.run 来更好地控制 ffmpeg 进程
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            self.logger.info(_("log_screenshot_taken", timestamp_sec, output_file))
            return True
        except FileNotFoundError:
            self.logger.error(_("error_ffmpeg_not_found"))
            # 可以在这里添加一个全局标志，以避免重复报告此错误
            return False
        except subprocess.CalledProcessError as e:
            self.logger.error(_("error_taking_screenshot", e))
            self.logger.error(f"ffmpeg stderr: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(_("error_taking_screenshot", e))
            return False

    def preview_anki_cards(self):
        """
        预览功能入口。
        收集UI参数并启动一个线程来生成HTML预览。
        """
        front_subtitle_file = self.front_subtitle_entry.get()
        back_subtitle_file = self.back_subtitle_entry.get()
        output_dir = self.output_dir_entry.get()

        if not front_subtitle_file or not back_subtitle_file:
            self.logger.error(_("error_preview_need_subs"))
            return
        if not output_dir:
            self.logger.error(_("error_preview_need_output_dir"))
            return

        self.preview_button["state"] = "disabled"

        anki_config=AnkiConfig()

        anki_config.output_dir=output_dir

        anki_config.add_ruby_front = self.add_ruby_front_var.get()
        anki_config.add_ruby_back = self.add_ruby_back_var.get()
        anki_config.clean_subtitle = self.clean_subtitle_var.get()
        anki_config.merge_subtitles = self.merge_subtitles_var.get()
        anki_config.merge_gap_ms = int(self.merge_gap_spinbox.get())

        anki_config.start_time_str = self.start_time_entry.get()
        anki_config.end_time_str = self.end_time_entry.get()

        anki_config.tts_engine = self.tts_engine_var.get()

        threading.Thread(
            target=self._preview_anki_thread,
            args=(front_subtitle_file, back_subtitle_file, anki_config),
            daemon=True
        ).start()

    def _preview_anki_thread(self, front_subtitle_file, back_subtitle_file, anki_config):
        """在后台线程中处理数据并生成HTML预览文件。"""
        try:
            self.root.after(0, lambda: self.logger.info(_("log_preview_generating")))

            front_subtitles = self.parse_srt_file(front_subtitle_file)
            back_subtitles = self.parse_srt_file(back_subtitle_file)

            # 应用时间段过滤
            front_subtitles = self._filter_subtitles_by_time(front_subtitles, anki_config.start_time_str, anki_config.end_time_str)
            back_subtitles = self._filter_subtitles_by_time(back_subtitles, anki_config.start_time_str, anki_config.end_time_str)

            # 应用字幕合并
            if anki_config.merge_subtitles:
                self.root.after(0, lambda: self.logger.info(_("log_merging_front_subs", anki_config.merge_gap_ms)))
                front_subtitles = self._merge_subtitles(front_subtitles, anki_config.merge_gap_ms)
                self.root.after(0, lambda: self.logger.info(_("log_merging_back_subs", anki_config.merge_gap_ms)))
                back_subtitles = self._merge_subtitles(back_subtitles, anki_config.merge_gap_ms)
            
            if not front_subtitles or not back_subtitles:
                self.root.after(0, lambda: self.logger.error(_("error_preview_no_subs")))
                return

            front_lang = self.detect_language_from_filename(front_subtitle_file)
            back_lang = self.detect_language_from_filename(back_subtitle_file)
            kks = None
            if 'ja' in [front_lang.lower(), back_lang.lower()]:
                try:
                    kks = pykakasi.kakasi()
                except Exception as e:
                    self.root.after(0, lambda: self.logger.error(_("error_init_pykakasi", e)))
            is_front_chinese = 'zh-hans' in front_lang.lower() or 'zh-hant' in front_lang.lower()
            is_back_chinese = 'zh-hans' in back_lang.lower() or 'zh-hant' in back_lang.lower()
            is_front_korean = 'ko' in front_lang.lower()
            is_back_korean = 'ko' in back_lang.lower()

            preview_cards_data = []
            total_segments = min(len(front_subtitles), len(back_subtitles))
            preview_limit = min(5, total_segments)

            if preview_limit == 0:
                self.root.after(0, lambda: self.logger.warning(_("warning_no_subs_for_preview")))
                return

            self.root.after(0, lambda: self.logger.info(_("log_processing_preview_cards", preview_limit)))

            for i in range(preview_limit):
                _front_start, _front_end, front_text = front_subtitles[i]
                _back_start, _back_end, back_text = back_subtitles[i]

                front_text = re.sub(r'<[^>]+>', '', front_text)
                back_text = re.sub(r'<[^>]+>', '', back_text)
                if anki_config.clean_subtitle:
                    non_dialogue_pattern = r'\[[^\]]*\]|\([^)]*\)|♪'
                    front_text = re.sub(non_dialogue_pattern, '', front_text)
                    back_text = re.sub(non_dialogue_pattern, '', back_text)
                front_text = ' '.join(front_text.split()).strip()
                back_text = ' '.join(back_text.split()).strip()

                if anki_config.add_ruby_front:
                    if kks and 'ja' in front_lang.lower():
                        front_text = add_furigana(kks, front_text)
                    elif is_front_chinese:
                        front_text = add_pinyin(front_text)
                    elif is_front_korean:
                        front_text = add_romanization_ko(front_text)
                
                if anki_config.add_ruby_back:
                    if kks and 'ja' in back_lang.lower():
                        back_text = add_furigana(kks, back_text)
                    elif is_back_chinese:
                        back_text = add_pinyin(back_text)
                    elif is_back_korean:
                        back_text = add_romanization_ko(back_text)

                if not front_text or not back_text: continue
                preview_cards_data.append({'Question': front_text, 'Answer': back_text})

            html_content = self._build_preview_html(preview_cards_data)

            # Ensure output directory exists before creating the preview file
            if not os.path.exists(anki_config.output_dir):
                try:
                    os.makedirs(anki_config.output_dir)
                    self.root.after(0, lambda: self.logger.info(_("log_created_download_dir", anki_config.output_dir)))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.logger.error(_("error_creating_download_dir", e)))
                    return # Stop if directory cannot be created

            preview_file_path = os.path.join(anki_config.output_dir, "anki_preview.html")
            with open(preview_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            webbrowser.open(preview_file_path)
            self.root.after(0, lambda: self.logger.info(_("log_preview_opened", preview_file_path)))

            # Store preview HTML file for cleanup on exit if option is enabled
            if self.cleanup_preview_html_var.get():
                self.preview_files_to_cleanup.append(preview_file_path)

        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_generating_preview", e)))
        finally:
            self.root.after(0, lambda: self.preview_button.configure(state="normal"))

    def _build_preview_html(self, cards_data):
        """根据卡片数据、模板和样式构建HTML内容。"""
        front_template = self.defaultPreviewConfig["anki_templates"]["front"]
        back_template = self.defaultPreviewConfig["anki_templates"]["back"]
        style = self.defaultPreviewConfig["anki_style"]
        preview_html_template = self.config["preview_html_template"]
        
        cards_html = ""
        for i, card_data in enumerate(cards_data):
            front_html = front_template.replace("{{Question}}", card_data['front_text'])
            back_html = back_template.replace("{{Answer}}", card_data['back_text'])
            cards_html += f"""
            <div class="card-container">
                <h2>{_("preview_card_title", i + 1)}</h2>
                <div class="card-side"><h3>{_("preview_card_front")}</h3><div class="card">{front_html}</div></div>
                <div class="card-side"><h3>{_("preview_card_back")}</h3><div class="card anki-back">{back_html}</div></div>
            </div><hr>"""

        return preview_html_template.replace("{{style}}", style).replace("{{cards_html}}", cards_html)

    def check_output_directory(self,output_dir:str):
        # 创建输出目录（如果不存在）
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.logger.info(_("log_created_download_dir", output_dir))
            except Exception as e:
                self.logger.error(_("error_creating_download_dir", e))
                return

    def generate_anki_package(self):
        # 获取输入参数
        media_file = self.media_entry.get()
        front_subtitle_file = self.front_subtitle_entry.get()
        back_subtitle_file = self.back_subtitle_entry.get()
        output_dir = self.output_dir_entry.get()
        anki_package_name = self.anki_package_name_entry.get()

        
        # 验证必要的输入
        if not front_subtitle_file:
            self.logger.error(_("error_need_front_sub"))
            return
        
        if not back_subtitle_file:
            self.logger.error(_("error_need_back_sub"))
            return
        
        if not output_dir:
            self.logger.error(_("error_need_output_dir"))
            return

        if not anki_package_name:
            self.logger.error(_("error_need_package_name"))
            return
        
        self.check_output_directory(output_dir)
        
        # 禁用生成按钮，防止重复点击
        self.generate_button["state"] = "disabled"

        anki_config=AnkiConfig()

        anki_config.media_file = media_file
        anki_config.output_dir = output_dir
        anki_config.anki_package_name = anki_package_name
        
        anki_config.add_ruby_front = self.add_ruby_front_var.get()
        anki_config.add_ruby_back = self.add_ruby_back_var.get()
        anki_config.slow_front = self.slow_front_tts_var.get()
        anki_config.slow_back = self.slow_back_tts_var.get()
        anki_config.clean_subtitle = self.clean_subtitle_var.get()
        anki_config.cleanup_mp3 = self.cleanup_mp3_var.get()
        anki_config.cleanup_csv = self.cleanup_csv_var.get()
        anki_config.cleanup_jpg = self.cleanup_jpg_var.get()
        anki_config.add_screenshot = self.add_screenshot_var.get()
        anki_config.screenshot_time = self.screenshot_time_var.get()
        anki_config.screenshot_quality = int(self.screenshot_quality_spinbox.get())
        anki_config.merge_subtitles = self.merge_subtitles_var.get()
        anki_config.merge_gap_ms = int(self.merge_gap_spinbox.get())

        anki_config.tts_engine=self.tts_engine_var.get()
        
        anki_config.start_time_str = self.start_time_entry.get()
        anki_config.end_time_str = self.end_time_entry.get()
        anki_config.overwrite_apkg = self.overwrite_apkg_var.get()

        try:
            timeline_offset_ms = int(self.offset_spinbox.get())
        except ValueError:
            self.logger.error(_("error_invalid_offset"))
            self.generate_button["state"] = "normal"
            return
        
        # 创建线程执行生成，避免界面卡顿
        threading.Thread(target=self._generate_anki_thread, args=( front_subtitle_file, back_subtitle_file, anki_config,), daemon=True).start()
    
    def _cleanup_temp_files(self, media_files_to_cleanup, csv_file_to_cleanup, screenshot_files_to_cleanup, anki_config):
        """清理生成过程中可能产生的临时文件。"""
        self.root.after(0, lambda: self.logger.info(_("log_cleaning_temp_files")))
        try:
            if anki_config.cleanup_mp3:
                # 清理音频文件
                for f in media_files_to_cleanup:
                    if os.path.exists(f):
                        os.remove(f)
                self.root.after(0, lambda: self.logger.info(_("log_cleaned_mp3")))
            
            if anki_config.cleanup_jpg:
                # 清理截图文件
                for f in screenshot_files_to_cleanup:
                    if os.path.exists(f):
                        os.remove(f)
                self.root.after(0, lambda: self.logger.info(_("log_cleaned_jpg")))

            if anki_config.cleanup_csv and csv_file_to_cleanup and os.path.exists(csv_file_to_cleanup):
                os.remove(csv_file_to_cleanup)
                self.root.after(0, lambda: self.logger.info(_("log_cleaned_csv")))
            
            if anki_config.cleanup_preview_html:
                preview_file = os.path.join(anki_config.output_dir, "anki_preview.html")
                if os.path.exists(preview_file):
                    os.remove(preview_file)
                    self.root.after(0, lambda: self.logger.info(_("log_cleaned_preview_html", preview_file)))

        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_cleaning_temp_files", e)))

    def _generate_anki_thread(self, front_subtitle_file, back_subtitle_file, anki_config):
        # 定义需要在 finally 块中访问的变量
        csv_file = os.path.join(anki_config.output_dir, "anki_cards.csv")
        media_files = []
        screenshot_files = []

        try:
            # 确保所有UI更新都在主线程执行
            self.root.after(0, lambda: self.logger.info(_("log_anki_generating")))
            self.root.after(0, lambda: self.progress_bar.configure(mode='determinate', value=0))
            # 将所有日志记录移到主线程执行
            self.root.after(0, lambda: [
                self.logger.info(f"{_('label_front_sub_file')} {front_subtitle_file}"),
                self.logger.info(f"{_('label_back_sub_file')} {back_subtitle_file}"),
                self.logger.info(f"{_('label_output_dir')} {anki_config.output_dir}"),
                (anki_config.media_file and 
                 self.logger.info(f"{_('label_media_file')} {anki_config.media_file}")),
                (anki_config.timeline_offset_ms != 0 and 
                 self.logger.info(_("log_timeline_offset", anki_config.timeline_offset_ms)))
            ])
            
            # 检查Anki包是否已存在且不允许覆盖
            output_apkg_path = os.path.join(anki_config.output_dir, f"{anki_config.anki_package_name}.apkg")
            if os.path.exists(output_apkg_path) and not anki_config.overwrite_apkg:
                self.root.after(0, lambda: self.logger.error(_("error_anki_pkg_exists", f"{anki_config.anki_package_name}.apkg")))
                return
            
             # 解析字幕文件
            front_subtitles = self.parse_srt_file(front_subtitle_file)
            back_subtitles = self.parse_srt_file(back_subtitle_file)

            # 应用时间段过滤
            front_subtitles = self._filter_subtitles_by_time(front_subtitles, anki_config.start_time_str, anki_config.end_time_str)
            back_subtitles = self._filter_subtitles_by_time(back_subtitles, anki_config.start_time_str, anki_config.end_time_str)

            # 如果提供了媒体文件，则预先加载到内存以提高效率
            main_audio_segment = None
            if anki_config.media_file and os.path.exists(anki_config.media_file) and (anki_config.tts_engine != "none"):
                self.root.after(0, lambda: self.logger.info(_("log_loading_media", anki_config.media_file)))
                try:
                    main_audio_segment = AudioSegment.from_file(anki_config.media_file)
                    # self.root.after(0, lambda: self.logger.info(_("log_media_loaded")))
                except Exception as e:
                    # self.root.after(0, lambda e=e: self.logger.error(_("error_loading_media", e)))
                    # 即使加载失败，也继续，后续会使用TTS
                    self.logger.error(_("error_loading_media", e))

           
            # 应用字幕合并
            if anki_config.merge_subtitles:
                self.root.after(0, lambda: self.logger.info(_("log_merging_front_subs", anki_config.merge_gap_ms)))
                front_subtitles = self._merge_subtitles(front_subtitles, anki_config.merge_gap_ms)
                self.root.after(0, lambda: self.logger.info(_("log_merging_back_subs", anki_config.merge_gap_ms)))
                back_subtitles = self._merge_subtitles(back_subtitles, anki_config.merge_gap_ms)
            
            if not front_subtitles or not back_subtitles:
                self.root.after(0, lambda: self.logger.error(_("error_parsing_subs_or_empty")))
                return
            
            # 检测语言
            front_lang = self.detect_language_from_filename(front_subtitle_file)
            back_lang = self.detect_language_from_filename(back_subtitle_file)
            
            self.logger.info(_("log_detected_front_lang", front_lang))
            self.logger.info(_("log_detected_back_lang", back_lang))
            
            # 如果检测到日语，初始化kakasi
            kks = None
            if 'ja' in [front_lang.lower(), back_lang.lower()]:
                try:
                    self.root.after(0, lambda: self.logger.info(_("log_ja_detected_init_kakasi")))
                    kks = pykakasi.kakasi()
                    self.root.after(0, lambda: self.logger.info(_("log_kakasi_initialized")))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.logger.error(_("error_init_kakasi", e)))

            # 检查是否需要添加中文注音
            is_front_chinese = 'zh' in front_lang.lower() 
            is_back_chinese = 'zh' in back_lang.lower() 
            if is_front_chinese or is_back_chinese:
                self.root.after(0, lambda: self.logger.info(_("log_zh_detected_add_pinyin")))

            # 新增：检查是否需要添加韩语罗马音
            is_front_korean = 'ko' in front_lang.lower()
            is_back_korean = 'ko' in back_lang.lower()
            if is_front_korean or is_back_korean:
                self.root.after(0, lambda: self.logger.info(_("log_ko_detected_add_romanization")))

            
            # 创建CSV文件
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Question", "Answer", "Audio_Question", "Audio_Answer", "Screenshot"])
                
                # 优化：减少进度条和日志更新频率
                last_progress_update = -1

                # 处理每个字幕片段
                total_segments = min(len(front_subtitles), len(back_subtitles))
                for i in range(total_segments):
                    # 更新进度条
                    current_progress = (i / total_segments) * 100
                    if current_progress - last_progress_update >= 1 or i == total_segments - 1: # Update every 1% or on last item
                        self.root.after(0, lambda p=current_progress: self.progress_bar.configure(value=p))
                        self.root.after(0, lambda p=current_progress: self.logger.info(_("log_generation_progress", p)))
                        last_progress_update = current_progress
                    
                    # 获取字幕文本
                    front_start, front_end, front_text = front_subtitles[i]
                    back_start, back_end, back_text = back_subtitles[i]
                    
                    # 清理文本：移除HTML标签
                    front_text = re.sub(r'<[^>]+>', '', front_text)
                    back_text = re.sub(r'<[^>]+>', '', back_text)

                    # 根据开关决定是否移除非对话内容
                    if anki_config.clean_subtitle:
                        non_dialogue_pattern = r'\[[^\]]*\]|\([^)]*\)|♪'
                        front_text = re.sub(non_dialogue_pattern, '', front_text)
                        back_text = re.sub(non_dialogue_pattern, '', back_text)
                    
                    # 清理多余空格
                    front_text = ' '.join(front_text.split()).strip()
                    back_text = ' '.join(back_text.split()).strip()

                    # 保存原始文本以用于TTS
                    front_text_for_tts = front_text
                    back_text_for_tts = back_text
                    
                    # 为日语文本添加注音
                    if anki_config.add_ruby_front and kks and 'ja' in front_lang.lower():
                        front_text = add_furigana(kks, front_text)
                    if anki_config.add_ruby_back and kks and 'ja' in back_lang.lower():
                        back_text = add_furigana(kks, back_text)

                    # 为中文文本添加拼音
                    if anki_config.add_ruby_front and is_front_chinese:
                        front_text = add_pinyin(front_text)
                    if anki_config.add_ruby_back and is_back_chinese:
                        back_text = add_pinyin(back_text)

                    # 新增：为韩语文本添加罗马音
                    if anki_config.add_ruby_front and is_front_korean:
                        front_text = add_romanization_ko(front_text)
                    if anki_config.add_ruby_back and is_back_korean:
                        back_text = add_romanization_ko(back_text)

                    if not front_text or not back_text:
                        continue
                    
                    front_audio_tag = ""
                    back_audio_tag = ""

                    if anki_config.tts_engine != "none":
                        # 生成音频文件名
                        front_audio = f"segment_front_{i+1:06d}.mp3"
                        back_audio = f"segment_back_{i+1:06d}.mp3"
                        
                        front_audio_path = os.path.join(anki_config.output_dir, front_audio)
                        back_audio_path = os.path.join(anki_config.output_dir, back_audio)
                        
                        # 生成正面音频
                        self._try_generate_audio_with_fallback(front_text_for_tts, anki_config.tts_engine,front_audio_path, front_lang, slow=anki_config.slow_front)
                        media_files.append(front_audio_path)
                        front_audio_tag = f"[sound:{front_audio}]"
                        
                        # 生成背面音频
                        if main_audio_segment:
                            # 应用时间轴偏移
                            adjusted_start = back_start + anki_config.timeline_offset_ms
                            adjusted_end = back_end + anki_config.timeline_offset_ms
                            # 从内存中的音频数据提取
                            
                            if not self.extract_audio_segment(main_audio_segment, adjusted_start, adjusted_end, back_audio_path):
                                self.logger.warning(_("warning_extract_audio_failed_tts_fallback", back_text_for_tts))
                                self.generate_tts_audio(back_text_for_tts, anki_config.tts_engine,back_audio_path, back_lang, slow=anki_config.slow_back)
                        else:
                            # 使用TTS生成音频
                            self.generate_tts_audio(back_text_for_tts,anki_config.tts_engine, back_audio_path, back_lang, slow=anki_config.slow_back)
                        
                        media_files.append(back_audio_path)
                        back_audio_tag = f"[sound:{back_audio}]"

                    # 新增：生成截图
                    screenshot_field = ""
                    video_extensions = ['.mp4', '.webm', '.avi', '.mkv']
                    if anki_config.add_screenshot and anki_config.media_file and any(anki_config.media_file.lower().endswith(ext) for ext in video_extensions):
                        screenshot_file = f"screenshot_{i+1:06d}.jpg"
                        screenshot_path = os.path.join(anki_config.output_dir, screenshot_file)
                        # 根据用户选择计算截图时间点
                        if anki_config.screenshot_time == _("screenshot_time_start"):
                            screenshot_time_ms = back_start + anki_config.timeline_offset_ms
                        elif anki_config.screenshot_time == _("screenshot_time_end"):
                            screenshot_time_ms = back_end + anki_config.timeline_offset_ms
                        else: # middle
                            screenshot_time_ms = back_start + (back_end - back_start) / 2 +anki_config. timeline_offset_ms
                        
                        if self.take_screenshot(anki_config.media_file, screenshot_time_ms, screenshot_path, quality=anki_config.screenshot_quality):
                            screenshot_field = f'<img src="{screenshot_file}">'
                            screenshot_files.append(screenshot_path)
                    
                    # 写入CSV
                    writer.writerow([front_text, back_text, front_audio_tag, back_audio_tag, screenshot_field])
            
            # 生成Anki包
            self.root.after(0, lambda: self.logger.info(_("log_generating_anki_pkg")))
            
            # 创建Anki模型
            model_id = random.randrange(1 << 30, 1 << 31)
            model = genanki.Model(
                model_id,
                _("anki_model_name"),
                fields=[
                    {'name': 'Question'},
                    {'name': 'Answer'},
                    {'name': 'Audio_Question'},
                    {'name': 'Audio_Answer'},
                    {'name': 'Screenshot'} # 新增截图字段
                ],
                templates=[
                    {
                        'name': _("anki_card_name"),
                        'qfmt': self.config["anki_templates"]["front"],
                        'afmt': self.config["anki_templates"]["back"],
                    },
                ],
                css=self.config["anki_style"]
            )
            
            # 创建Anki牌组
            deck_id = random.randrange(1 << 30, 1 << 31)
            deck = genanki.Deck(deck_id, anki_config.anki_package_name)
            
            # 从CSV文件读取数据并添加到牌组
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过标题行
                for row in reader:
                    if len(row) >= 5:
                        note = genanki.Note(
                            model=model,
                            fields=[row[0], row[1], row[2], row[3], row[4]]
                        )
                        deck.add_note(note)
            
            # 创建包含媒体文件的Anki包
            package = genanki.Package(deck)
            package.media_files = media_files + screenshot_files
            
            # 保存Anki包
            output_file = os.path.join(anki_config.output_dir, f"{anki_config.anki_package_name}.apkg")
            package.write_to_file(output_file)
            
            # 更新UI
            self.root.after(0, lambda: self.progress_bar.configure(value=100))
            self.root.after(0, lambda: self.logger.info(_("log_anki_pkg_complete", output_file)))

        except Exception as e:
            self.root.after(0, lambda e=e: self.logger.error(_("error_generating_anki_pkg", e)))
        finally:
            # 清理中间文件（无论成功或失败）
            if anki_config.cleanup_mp3 or anki_config.cleanup_csv or anki_config.cleanup_jpg:
                self.root.after(0, lambda: self.logger.info(_("log_cleaning_temp_files")))
                try:
                    if anki_config.cleanup_mp3:
                        for f in media_files:
                            if os.path.exists(f): os.remove(f)
                        self.root.after(0, lambda: self.logger.info(_("log_cleaned_mp3")))
                    if anki_config.cleanup_jpg:
                        for f in screenshot_files:
                            if os.path.exists(f): os.remove(f)
                        self.root.after(0, lambda: self.logger.info(_("log_cleaned_jpg")))
                    if anki_config.cleanup_csv:
                        if os.path.exists(csv_file): os.remove(csv_file)
                        self.root.after(0, lambda: self.logger.info(_("log_cleaned_csv")))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.logger.error(_("error_cleaning_temp_files", e)))

            # 恢复生成按钮状态
            self.root.after(0, lambda: self.generate_button.configure(state="normal"))

            # 清除时间范围输入框
            self.root.after(0, lambda: self.start_time_entry.delete(0, tk.END))
            self.root.after(0, lambda: self.end_time_entry.delete(0, tk.END))
            
    def load_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 用加载的配置更新默认配置。
                    # 这允许加载像 "language" 这样不在初始字典中的新键，从而修复了启动时不加载语言设置的错误。
                    self.config.update(loaded_config)
                self.logger.info(_("log_config_loaded")) if hasattr(self, 'logger') else None
            except Exception as e:
                print(_("error_loading_config", e))
    
    def on_closing(self):
        # 程序关闭时保存配置
        self.save_config()
        self.root.destroy()
        
        # 删除所有预览文件
        preview_files = glob.glob(os.path.join(self.config["download_directory"], "output", "anki_preview.html"))
        for file_path in preview_files:
            try:
                os.remove(file_path)
                self.logger.info(_("log_deleted_preview_file", file_path))
            except Exception as e:
                self.logger.error(_("error_deleting_preview_file", e))
