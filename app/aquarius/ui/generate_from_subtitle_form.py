from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QMainWindow, 
                              QMenuBar, QTabWidget, QMessageBox, QPushButton, 
                              QComboBox, QLineEdit, QFileDialog,QCheckBox,QSpinBox,QDialog,QTextEdit,QTimeEdit)
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QObject, Signal, Slot, QThread
from ui.helper import add_lang_to_combo_box,restore_lang_combobox,add_tts_engine_to_combobox,is_media_file_tts,add_data_to_combobox_item,add_image_creator_combobox,find_required_child
from ui.qt_progress import Progress,QtProgress

import tempfile
import os
import webbrowser
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from typing import Optional

from service.resource_manager import get_app_config,load_config,add_temp_file,save_last_media_folder,save_download_folder
from entity.config_def import SubtitleConfig,BaseAnkiConfig
from entity.config_sync import sync_subtitle_config_from_ui
from service.anki_generator import BaseAnkiGenerator,SubtitleAnkiGenerator
from entity.anki_card import AnkiCard
from service.tts_generator import AudioGeneratorFactory, BaseAudioGenerator, FileAudioGenerator

from ui.base_generate_from import BaseFormController,show_html_preview_dialog,create_anki_cards

from PySide6.QtCore import QCoreApplication
tr = QCoreApplication.translate  # 将 translate 重命名为 tr

class GenerateFromSubtitleFormController(BaseFormController):
    def __init__(self, generate_from_subtitle_form: QWidget, progress: Progress):
        super().__init__(generate_from_subtitle_form, progress)
        self.generate_from_subtitle_form:QWidget = generate_from_subtitle_form
        self.progress = progress
        
        self.subtitle_config: SubtitleConfig = SubtitleConfig()

        self._fetch_children()

        self._init_widget_values()
        self._connect_signals()
    
    def sync_subtitle_config_to_widget(self, subtitle_config: SubtitleConfig):
        """接收从 DownloadFormController 发来的 subtitle_config 并同步 UI"""
        
        # 示例：填充媒体文件路径
        if subtitle_config.media_file:
            self.media_file_edit.setText(subtitle_config.media_file)

        if subtitle_config.front_subtitle_file:
            self.front_subtitle_file_edit.setText(subtitle_config.front_subtitle_file)

            anki_package_name=os.path.basename(subtitle_config.front_subtitle_file).split('.')[0]
            self.anki_package_name_edit.setText(anki_package_name)

        if subtitle_config.back_subtitle_file:
            self.back_subtitle_file_edit.setText(subtitle_config.back_subtitle_file)

        # 同步正面字幕语言
        restore_lang_combobox(subtitle_config.front_lang, self.front_lang_combobox)

        # 同步背面字幕语言
        restore_lang_combobox(subtitle_config.back_lang, self.back_lang_combobox)

    def _fetch_children(self):
        # QLineEdit
        self.media_file_edit = find_required_child(self.generate_from_subtitle_form,QLineEdit, "media_file_edit")
        self.front_subtitle_file_edit = find_required_child(self.generate_from_subtitle_form,QLineEdit, "front_subtitle_file_edit")
        self.back_subtitle_file_edit = find_required_child(self.generate_from_subtitle_form,QLineEdit, "back_subtitle_file_edit")
        self.output_folder_edit = find_required_child(self.generate_from_subtitle_form,QLineEdit, "output_folder_edit")
        self.anki_package_name_edit = find_required_child(self.generate_from_subtitle_form,QLineEdit, "anki_package_name_edit")

        # QComboBox
        self.screenshot_source_combobox = find_required_child(self.generate_from_subtitle_form,QComboBox, "screenshot_source_combobox")
        self.front_lang_combobox = find_required_child(self.generate_from_subtitle_form,QComboBox, "front_lang_combobox")
        self.front_subtitle_audio_engine_combobox = find_required_child(self.generate_from_subtitle_form,QComboBox, "front_subtitle_audio_engine_combobox")
        self.back_lang_combobox = find_required_child(self.generate_from_subtitle_form,QComboBox, "back_lang_combobox")
        self.back_subtitle_audio_engine_combobox = find_required_child(self.generate_from_subtitle_form,QComboBox, "back_subtitle_audio_engine_combobox")
        self.screenshot_period_combobox = find_required_child(self.generate_from_subtitle_form,QComboBox, "screenshot_period_combobox")
        self.screenshot_quality_combobox = find_required_child(self.generate_from_subtitle_form,QComboBox, "screenshot_quality_combobox")

        
        screenshot_period :list = [QCoreApplication.translate("generate_from_subttitle_form","begin"),
                                   QCoreApplication.translate("generate_from_subttitle_form","middle"),
                                   QCoreApplication.translate("generate_from_subttitle_form","end")]
        add_data_to_combobox_item(self.screenshot_period_combobox, screenshot_period)

        screenshot_quality :list = [QCoreApplication.translate("generate_from_subttitle_form","low"),
                                   QCoreApplication.translate("generate_from_subttitle_form","medium"),
                                   QCoreApplication.translate("generate_from_subttitle_form","high")]
        add_data_to_combobox_item(self.screenshot_quality_combobox, screenshot_quality) 

        self.screenshot_quality_combobox.setCurrentIndex(1)

        # QCheckBox
        
        self.subtitle_clean_checkbox = find_required_child(self.generate_from_subtitle_form,QCheckBox, "subtitle_clean_checkbox")
        self.front_ruby_checkbox = find_required_child(self.generate_from_subtitle_form,QCheckBox, "front_ruby_checkbox")
        self.back_ruby_checkbox = find_required_child(self.generate_from_subtitle_form,QCheckBox, "back_ruby_checkbox")
        self.front_subtitle_audio_slow_checkbox= find_required_child(self.generate_from_subtitle_form,QCheckBox, "front_subtitle_audio_slow_checkbox")
        self.back_subtitle_audio_slow_checkbox= find_required_child(self.generate_from_subtitle_form,QCheckBox, "back_subtitle_audio_slow_checkbox")
        self.overwrite_target_checkbox = find_required_child(self.generate_from_subtitle_form,QCheckBox, "overwrite_target_checkbox")
        self.cleanup_audio_checkbox = find_required_child(self.generate_from_subtitle_form,QCheckBox, "cleanup_audio_checkbox")
        self.cleanup_csv_checkbox = find_required_child(self.generate_from_subtitle_form,QCheckBox, "cleanup_csv_checkbox")
        self.cleanup_image_checkbox = find_required_child(self.generate_from_subtitle_form,QCheckBox, "cleanup_image_checkbox")

        # QSpinBox
        self.front_subtitle_audio_offset_spinbox = find_required_child(self.generate_from_subtitle_form,QSpinBox, "front_subtitle_audio_offset_spinbox")
        self.back_subtitle_audio_offset_spinbox = find_required_child(self.generate_from_subtitle_form,QSpinBox, "back_subtitle_audio_offset_spinbox")
        self.time_range_start_timeedit = find_required_child(self.generate_from_subtitle_form,QTimeEdit, "time_range_start_timeedit")
        self.time_range_end_timeedit = find_required_child(self.generate_from_subtitle_form,QTimeEdit, "time_range_end_timeedit")

        # QPushButton
        self.media_file_button = find_required_child(self.generate_from_subtitle_form,QPushButton, "media_file_button")
        self.front_subtitle_file_button = find_required_child(self.generate_from_subtitle_form,QPushButton, "front_subtitle_file_button")
        self.back_subtitle_file_button = find_required_child(self.generate_from_subtitle_form,QPushButton, "back_subtitle_file_button")
        self.output_folder_button = find_required_child(self.generate_from_subtitle_form,QPushButton, "output_folder_button")
        self.preview_button = find_required_child(self.generate_from_subtitle_form,QPushButton, "preview_button")
        self.generate_button = find_required_child(self.generate_from_subtitle_form,QPushButton, "generate_button")


    def _init_widget_values(self):
        
        app_config = get_app_config()

        add_lang_to_combo_box(self.front_lang_combobox)
        add_lang_to_combo_box(self.back_lang_combobox)

        restore_lang_combobox(app_config.default_front_lang,self.front_lang_combobox)
        restore_lang_combobox(app_config.default_back_lang,self.back_lang_combobox)

        add_tts_engine_to_combobox(self.front_subtitle_audio_engine_combobox)
        add_tts_engine_to_combobox(self.back_subtitle_audio_engine_combobox)    

        original_text=QCoreApplication.translate("generate_from_subttitle_form","orginal")
        self.front_subtitle_audio_engine_combobox.insertItem(0, original_text, "orginal")    
        self.back_subtitle_audio_engine_combobox.insertItem(0, original_text, "orginal")    

        engine_str=QCoreApplication.translate("generate_from_subtitle_form", "image search engines")
        add_image_creator_combobox(engine_str, self.screenshot_source_combobox)


    def _connect_signals(self):
        self.media_file_button.clicked.connect(self._on_media_file_button_clicked)
        self.front_subtitle_file_button.clicked.connect(self._on_front_subtitle_file_button_clicked)
        self.back_subtitle_file_button.clicked.connect(self._on_back_subtitle_file_button_clicked)
        self.output_folder_button.clicked.connect(self._on_output_folder_button_clicked)
        self.preview_button.clicked.connect(self._on_preview_button_clicked)
        self.generate_button.clicked.connect(self._on_generate_button_clicked)
            

    def _on_front_subtitle_file_button_clicked(self):
        # 更新文件过滤器以包含 .vtt 文件
        file_name, _ = QFileDialog.getOpenFileName(
            self.generate_from_subtitle_form, 
            QCoreApplication.translate("generate_from_subttitle_form","select front subtitle file"), 
            "", 
            QCoreApplication.translate("generate_from_subttitle_form","Subtitle Files (*.srt *.vtt)")
        )
        
        if file_name:
            self.front_subtitle_file_edit.setText(file_name)
            if self.anki_package_name_edit.text().strip()=="":
                anki_package_name=os.path.basename(file_name).split('.')[0]
                self.anki_package_name_edit.setText(anki_package_name)

            if self.output_folder_edit.text().strip()=="":
                self.output_folder_edit.setText(os.path.join(os.path.dirname(file_name), "anki_package"))

    def _on_back_subtitle_file_button_clicked(self):
        # 更新文件过滤器以包含 .vtt 文件
        file_name, _ = QFileDialog.getOpenFileName(
            self.generate_from_subtitle_form, 
            QCoreApplication.translate("generate_from_subttitle_form","select back subtitle file"), 
            "", 
            QCoreApplication.translate("generate_from_subttitle_form","Subtitle Files (*.srt *.vtt)")
        )
        if file_name:
            self.back_subtitle_file_edit.setText(file_name)

    def _on_media_file_button_clicked(self):
        # 打开文件选择框 选择*.srt 文件
        dialog_title=QCoreApplication.translate("generate_from_subttitle_form","select multimedia files")
        dialog_filter=QCoreApplication.translate("generate_from_subttitle_form","Multimedia files (*.mp4 *.mp3 *.webm *.mkv *.m4a *.wav *wmv *.wma)")
        
        file_name, _ = QFileDialog.getOpenFileName(self.generate_from_subtitle_form, dialog_title,filter=dialog_filter,dir=get_app_config().last_media_folder)
        if file_name:
            self.media_file_edit.setText(file_name)            

            # 获取文件所在目录
            directory = os.path.dirname(file_name)
            
            anki_package_name=os.path.basename(file_name).split('.')[0]

            self.anki_package_name_edit.setText(anki_package_name)
            self.output_folder_edit.setText(os.path.join(directory, "anki_package"))

            save_last_media_folder(directory)

            # 根据媒体文件名和默认的语言名称在相同目录下查找subtitle文件，然后填充到front_subtitle_file_edit和back_subtitle_file_edit

            # 获取默认语言名称
            app_config = get_app_config()
            front_lang = app_config.default_front_lang
            back_lang = app_config.default_back_lang

            base_name = os.path.splitext(os.path.basename(file_name))[0]

            # 构建字幕文件名（先尝试 .srt 后尝试 .vtt）
            front_subtitle_file_srt = os.path.join(directory, f"{base_name}.{front_lang}.srt")
            front_subtitle_file_vtt = os.path.join(directory, f"{base_name}.{front_lang}.vtt")
            back_subtitle_file_srt = os.path.join(directory, f"{base_name}.{back_lang}.srt")
            back_subtitle_file_vtt = os.path.join(directory, f"{base_name}.{back_lang}.vtt")

            # 检查文件是否存在并填充到对应的 QLineEdit
            if os.path.exists(front_subtitle_file_srt):
                self.front_subtitle_file_edit.setText(front_subtitle_file_srt)
            elif os.path.exists(front_subtitle_file_vtt):
                self.front_subtitle_file_edit.setText(front_subtitle_file_vtt)
            else:
                self.front_subtitle_file_edit.clear()

            if os.path.exists(back_subtitle_file_srt):
                self.back_subtitle_file_edit.setText(back_subtitle_file_srt)
            elif os.path.exists(back_subtitle_file_vtt):
                self.back_subtitle_file_edit.setText(back_subtitle_file_vtt)
            else:
                self.back_subtitle_file_edit.clear()
    
    def _on_output_folder_button_clicked(self):
        folder_name = QFileDialog.getExistingDirectory(self.generate_from_subtitle_form, QCoreApplication.translate("generate_from_subttitle_form","Select output folder"))
        if folder_name:
            self.output_folder_edit.setText(folder_name)
        

    def _create_anki_generator(self) -> BaseAnkiGenerator:
        sync_subtitle_config_from_ui(self.generate_from_subtitle_form, self.subtitle_config)

        self.subtitle_config.front_template=get_app_config().front_template
        self.subtitle_config.back_template=get_app_config().back_template
        self.subtitle_config.anki_style=get_app_config().anki_style

        anki_generaotr: BaseAnkiGenerator =  SubtitleAnkiGenerator(self.subtitle_config)
        return anki_generaotr

    def sync_configuration(self ) -> BaseAnkiConfig:
        sync_subtitle_config_from_ui(self.generate_from_subtitle_form, self.subtitle_config)
        return self.subtitle_config
            
    def get_anki_config(self) -> BaseAnkiConfig:
        return self.subtitle_config
        
    def check_condition(self, parent_widget: QWidget,anki_config :BaseAnkiConfig,progress:Progress) -> bool:
        
        if not ( os.path.exists(self.subtitle_config.front_subtitle_file) and os.path.exists(self.subtitle_config.back_subtitle_file)):
            QMessageBox.critical(parent_widget, QCoreApplication.translate("base_form","error"), QCoreApplication.translate("generate_from_subtitle_form","Please select two subtitle files."))            
            return False
        
        return super().check_condition(parent_widget,anki_config,progress)

        

