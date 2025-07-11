import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import locale
import localization # Import the whole module to access localization.LANGUAGES
from localization import (
    get_locale_string as _,
    set_language,
    get_lang_display,
    get_available_languages,
    get_available_display_languages,
    LANG_DISPLAY_NAMES
)

import pykakasi

# 添加中文拼音支持
from pypinyin import pinyin, Style

# 新增：添加韩语罗马音支持
from korean_romanizer.romanizer import Romanizer
import re


class Start:
    should_continue=True

    def __init__(self, master): # 接受master参数
        self.master = master
        self.config_path = "config.json"
        self.config = self._load_config()
        self.config_updated_and_saved = False

        # --- NEW LOGIC STARTS HERE ---
        # Detect system language and set application's display language

        self.init_default_lang()
        

        # Check if preferred languages are set
        front_lang_set = self.config.get("preferred_front_language") and self.config.get("preferred_front_language") != ""
        back_lang_set = self.config.get("preferred_back_language") and self.config.get("preferred_back_language") != ""

        if not front_lang_set or not back_lang_set:
            self.should_continue=False
            self._show_setup_ui()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror(_("app_title"), _("error_config_corrupted"))
                return {}
        return {}

    def _save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            self.config_updated_and_saved = True
            # messagebox.showinfo(_("app_title"), _("config_saved_restart"))
        except Exception as e:
            messagebox.showerror(_("app_title"), _("error_saving_config", e))

    def _show_setup_ui(self):
        self.setup_window = tk.Toplevel(self.master) # 将master传递给Toplevel
        self.setup_window.title(_("welcome_title"))
        self.setup_window.geometry("320x400")
        self.setup_window.resizable(False, False)
        self.setup_window.grab_set() # Make window modal

        frame = ttk.Frame(self.setup_window, padding="20")
        frame.pack(expand=True, fill="both")

        # Welcome message
        self.welcome_message_label = ttk.Label(frame, text=_("welcome_message"), wraplength=450, justify="left")
        self.welcome_message_label.pack(pady=10)

        # Language selection
        self.display_language_label = ttk.Label(frame, text=_("select_display_language"))
        self.display_language_label.pack(pady=(10, 0))
        self.display_lang_var = tk.StringVar()
        self.display_lang_combobox = ttk.Combobox(frame, textvariable=self.display_lang_var, state="readonly")
        
        display_language_options = [get_lang_display(code) for code in get_available_languages().keys()]
        self.display_lang_combobox['values'] = display_language_options
        
        # Set initial value to current app display language
        current_app_lang_code = localization.translator.lang
        self.display_lang_var.set(get_lang_display(current_app_lang_code))

        self.display_lang_combobox.pack(pady=5)
        self.display_lang_combobox.bind("<<ComboboxSelected>>", self._on_display_language_selected)

        # Front language selection
        self.front_lang_label = ttk.Label(frame, text=_("select_front_lang"))
        self.front_lang_label.pack(pady=(10, 0))
        self.front_lang_var = tk.StringVar()
        self.front_lang_combobox = ttk.Combobox(frame, textvariable=self.front_lang_var, state="readonly")
        
        available_languages = get_available_languages()
        display_languages = [get_lang_display(code) for code in available_languages.keys()]
        self.front_lang_combobox['values'] = display_languages
        self.front_lang_combobox.pack(pady=5)

        # Back language selection
        self.back_lang_label = ttk.Label(frame, text=_("select_back_lang"))
        self.back_lang_label.pack(pady=(10, 0))
        self.back_lang_var = tk.StringVar()
        self.back_lang_combobox = ttk.Combobox(frame, textvariable=self.back_lang_var, state="readonly")
        self.back_lang_combobox['values'] = display_languages
        self.back_lang_combobox.pack(pady=5)

        def on_continue():
            selected_front_display = self.front_lang_var.get()
            selected_back_display = self.back_lang_var.get()

            if not selected_front_display or not selected_back_display:
                messagebox.showerror(_("app_title"), _("error_select_both_langs"))
                return

            # Convert display names back to language codes
            front_lang_code = ""
            back_lang_code = ""
            for code, display_name in available_languages.items():
                if get_lang_display(code) == selected_front_display:
                    front_lang_code = code
                if get_lang_display(code) == selected_back_display:
                    back_lang_code = code
            
            if not front_lang_code or not back_lang_code:
                messagebox.showerror(_("app_title"), "Internal error: Could not map selected language display names to codes.")
                return

            if front_lang_code == back_lang_code:
                messagebox.showwarning(_("app_title"), _("warning_same_subtitle_language"))
                # Find an alternative language for back_lang_code
                alternative_back_lang_code = None
                for code in available_languages.keys():
                    if code != front_lang_code:
                        alternative_back_lang_code = code
                        break
                
                if alternative_back_lang_code:
                    back_lang_code = alternative_back_lang_code
                    self.back_lang_var.set(get_lang_display(back_lang_code))
                else:
                    messagebox.showerror(_("app_title"), _("error_no_alternative_language"))
                    return

            self.config["preferred_front_language"] = front_lang_code
            self.config["preferred_back_language"] = back_lang_code
            self._save_config()
            self.should_continue=True # Set to True if user continues
            self.setup_window.destroy()

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        self.continue_button = ttk.Button(button_frame, text=_("button_continue"), command=on_continue)
        self.continue_button.pack(side=tk.LEFT, padx=5)

        def on_cancel():
            self.should_continue=False # Set to False if user cancels
            self.setup_window.destroy()

        self.cancel_button = ttk.Button(button_frame, text=_("button_cancel"), command=on_cancel)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        self.setup_window.wait_window() # Wait for the setup window to close

    def _on_display_language_selected(self, event):
        selected_display_name = self.display_lang_var.get()
        selected_lang_code = ""
        for code, display_name in get_available_languages().items():
            if get_lang_display(code) == selected_display_name:
                selected_lang_code = code
                break
        
        if selected_lang_code:
            set_language(selected_lang_code)
            self._update_setup_ui_text()

    def init_default_lang(self):
        system_locale = locale.getdefaultlocale()[0] # e.g., 'en_US', 'zh_CN'
        app_display_lang_code = "en" # Default fallback

        if system_locale:
            # Try exact match first (e.g., 'zh_CN' -> 'zh-Hans')
            # Iterate through LANGUAGES in localization.py to find a match
            # LANGUAGES = {"en": "English", "zh-Hans": "简体中文 (Simplified)", ...}
            for code in localization.LANGUAGES.keys(): # Access LANGUAGES directly from localization
                if code.lower() == system_locale.replace('_', '-').lower():
                    app_display_lang_code = code
                    break
            # If no exact match, try matching by primary language (e.g., 'en_US' -> 'en')
            if app_display_lang_code == "en": # Only if not already matched
                primary_lang = system_locale.split('_')[0].lower()
                for code in localization.LANGUAGES.keys():
                    if code.split('-')[0].lower() == primary_lang:
                        app_display_lang_code = code
                        break

        # Set the application's display language
        localization.set_language(app_display_lang_code)
        # --- NEW LOGIC ENDS HERE --- # Flag to indicate if config was updated and saved

    def _update_setup_ui_text(self):
        # Update welcome message
        self.setup_window.title(_("welcome_title"))
        self.welcome_message_label.config(text=_("welcome_message"))
        self.display_language_label.config(text=_("select_display_language"))
        self.front_lang_label.config(text=_("select_front_lang"))
        self.back_lang_label.config(text=_("select_back_lang"))
        self.continue_button.config(text=_("button_continue"))
        self.cancel_button.config(text=_("button_cancel"))

        # Re-populate combobox values with new language display names
        display_language_options = [get_lang_display(code) for code in get_available_languages().keys()]
        self.display_lang_combobox['values'] = display_language_options
        self.front_lang_combobox['values'] = display_language_options
        self.back_lang_combobox['values'] = display_language_options

        # Set current selections to reflect new language
        current_front_code = self.config.get("preferred_front_language", "")
        current_back_code = self.config.get("preferred_back_language", "")
        self.front_lang_var.set(get_lang_display(current_front_code) if current_front_code else "")
        self.back_lang_var.set(get_lang_display(current_back_code) if current_back_code else "")
        self.display_lang_var.set(get_lang_display(localization.translator.lang))

def add_pinyin(text):
    """使用 pypinyin 为中文文本添加注音（Pinyin）"""
    if not text:
        return ""
    try:
        # 使用正则表达式查找所有连续的中文字符串
        chinese_char_pattern = re.compile(r'[一-鿿]+')
        
        parts = []
        last_end = 0
        for match in chinese_char_pattern.finditer(text):
            # 添加当前匹配前的非中文字符串
            parts.append(text[last_end:match.start()])
            
            # 处理中文字符串
            chinese_segment = match.group(0)
            # 获取带声调的拼音
            pinyin_result = pinyin(chinese_segment, style=Style.TONE)
            
            ruby_segment = ""
            for i, char in enumerate(chinese_segment):
                pinyin_for_char = pinyin_result[i][0]
                ruby_segment += f"<ruby>{char}<rt>{pinyin_for_char}</rt></ruby>"
            parts.append(ruby_segment)
            
            last_end = match.end()
            
        # 添加最后一个匹配后的非中文字符串
        parts.append(text[last_end:])
        
        return "".join(parts)
    except Exception as e:
        # In a real application, you might want to log this error
        # print(f"Warning: Failed to add pinyin to '{text}': {e}")
        return text # 发生错误时返回原文


def add_furigana(kks, text):
    """使用pykakasi为日文文本添加注音（Furigana）"""
    if not text:
        return ""
    try:
        result = kks.convert(text)
        furigana_text = []
        for item in result:
            orig = item['orig']
            hira = item['hira']
            # 当原文和读音不同，且包含汉字时，添加注音
            if orig != hira and any('\u4e00' <= char <= '\u9fff' for char in orig):
                # 使用<ruby>标签格式: <ruby>漢字<rt>かんじ</rt></ruby>
                furigana_text.append(f"<ruby>{orig}<rt>{hira}</rt></ruby>")
            else:
                furigana_text.append(orig)
        return ''.join(furigana_text)
    except Exception as e:
        # 可以添加日志记录或错误处理
        return text  # 返回原始文本作为回退

def add_romanization_ko(text):
    """使用 korean-romanizer 为韩文文本添加罗马音"""
    if not text:
        return ""
    try:
        # 匹配韩文字符的正则表达式
        hangul_pattern = re.compile(r'[가-힣]+')
        
        parts = []
        last_end = 0
        for match in hangul_pattern.finditer(text):
            # 添加非韩文部分
            parts.append(text[last_end:match.start()])
            
            # 处理韩文部分
            hangul_segment = match.group(0)
            # 使用库进行转换
            romanized_segment = Romanizer(hangul_segment).romanize()
            
            # 使用<ruby>标签包裹
            parts.append(f"<ruby>{hangul_segment}<rt>{romanized_segment}</rt></ruby>")
            
            last_end = match.end()
        
        # 添加末尾的非韩文部分
        parts.append(text[last_end:])
        
        return "".join(parts)
    except Exception as e:
        # In a real application, you might want to log this error
        # print(f"Warning: Failed to add Korean romanization to '{text}': {e}")
        return text # 发生错误时返回原文
