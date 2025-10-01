import sys
import os
import json

from PySide6.QtWidgets import QComboBox,QWidget,QMessageBox
from PySide6.QtCore import QFile, QObject, Signal, Slot, QThread,QUrl
from PySide6.QtGui import QDesktopServices

import tempfile
from typing import Optional
from util.localization import get_available_display_languages
from service.resource_manager import get_app_config, save_config,add_temp_file
from entity.anki_card import AnkiCard

from ui.qt_progress import Progress,QtProgress

from service.anki_generator import BaseAnkiGenerator,SubtitleAnkiGenerator
from service.tts_generator import AudioGeneratorFactory, BaseAudioGenerator, FileAudioGenerator
from service.image_generator import BaseImageCreator, FfmpegImageCreator
from entity.config_def import SubtitleConfig,BaseAnkiConfig


from typing import TypeVar, cast

T = TypeVar('T')




def find_required_child(widget, child_type: type[T], object_name: str) -> T:
    child = widget.findChild(child_type, object_name)
    if child is None:
        raise RuntimeError(f"Failed to find required UI element: {object_name}")
    return cast(T, child)


def add_tts_engine_to_combobox(tts_engine_combobox: QComboBox):
    tts_engines :dict = {        
        "gtts": "gtts",
        "edge-tts": "edge-tts",
        "pyttsx3": "pyttsx3", 
        "none": "none"
    }

    for name, code in tts_engines.items():
        tts_engine_combobox.addItem(name, code)
    
    app_config=get_app_config()
    tts_engine_combobox.setCurrentIndex(tts_engine_combobox.findData(app_config.default_tts))

def add_dict_to_combobox_item(combo_box: QComboBox, mapping: dict): 
     for name, code in mapping.items():
        combo_box.addItem(name, code)   

def add_data_to_combobox_item(combo_box: QComboBox, datas: list[str]): 
     for name in datas:
        combo_box.addItem(name)   

def is_media_file_tts(tts_engine) -> bool:
    if isinstance(tts_engine, QComboBox):
        return tts_engine.currentData() == "orginal"
    elif isinstance(tts_engine, str):
        return tts_engine == "orginal"
    return False

def add_lang_to_combo_box(lang_combobox: QComboBox):

    display_languages = get_available_display_languages()
    app_config = get_app_config()
    # front
    lang_combobox.clear()
    for lang_code, display_name in display_languages.items():
        lang_combobox.addItem(display_name, lang_code)


def restore_lang_combobox(lang:str, lang_combobox: QComboBox):
    # The default for findData is case-sensitive. Make it explicitly case-insensitive for consistency.
    if _restore_lang_combobox(lang, lang_combobox):
        return
    
    if not lang:
        return
    
    if "-" in lang:
        new_lang=lang.split("-")[0]
        if _restore_lang_combobox(new_lang, lang_combobox):
            return
    
    if "_" in lang:
        new_lang=lang.split("_")[0]
        _restore_lang_combobox(new_lang, lang_combobox)

def _restore_lang_combobox(lang, lang_combobox) -> bool:
    if lang:
        for i in range(lang_combobox.count()):
            data = lang_combobox.itemData(i)
            if isinstance(data, str) and data.lower() == lang.lower():
                lang_combobox.setCurrentIndex(i)
                return True

    return False

def add_image_creator_combobox(engine_str: str, image_creator_combobox: QComboBox):
    engines = json.loads(engine_str)

    for key, value in engines.items():
        image_creator_combobox.addItem(key, value)