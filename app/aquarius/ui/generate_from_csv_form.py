import os

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QMainWindow, 
                              QMenuBar, QTabWidget, QMessageBox, QPushButton, 
                              QComboBox, QLineEdit, QFileDialog,QCheckBox)
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QObject, Signal, Slot, QThread
from ui.helper import add_lang_to_combo_box,restore_lang_combobox,add_tts_engine_to_combobox,is_media_file_tts,add_image_creator_combobox,find_required_child
from ui.qt_progress import Progress,QtProgress
from service.resource_manager import get_app_config,load_config,add_temp_file,save_last_media_folder,save_download_folder,is_blank
from entity.config_sync import sync_csv_config_from_ui
from entity.config_def import BaseAnkiConfig, CsvConfig
from service.anki_generator import BaseAnkiGenerator,CsvAnkiGenerator


from PySide6.QtCore import QCoreApplication
tr = QCoreApplication.translate  # 将 translate 重命名为 tr

from ui.base_generate_from import BaseFormController,create_anki_cards,show_html_preview_dialog

class GenerateFromCsvFormController(BaseFormController):
    def __init__(self, generate_from_csv_form: QWidget, progress: Progress):
        super().__init__(generate_from_csv_form, progress)
        self.generate_from_csv_form :QWidget = generate_from_csv_form
        self.progress = progress

        self.csv_config: CsvConfig = CsvConfig()

        self._fetch_children()
        self._init_widget_values()
        self._connect_signals()
    
    def _fetch_children(self):
        # 文件路径相关
        self.csv_file_edit: QLineEdit = find_required_child(self.generate_from_csv_form,QLineEdit, 'csv_file_edit')
        self.csv_file_button: QPushButton = find_required_child(self.generate_from_csv_form,QPushButton, 'csv_file_button')
        self.output_folder_edit: QLineEdit = find_required_child(self.generate_from_csv_form,QLineEdit, 'output_folder_edit')
        self.output_folder_button: QPushButton = find_required_child(self.generate_from_csv_form,QPushButton, 'output_folder_button')
        self.anki_package_name_edit: QLineEdit = find_required_child(self.generate_from_csv_form,QLineEdit, 'anki_package_name_edit')

        # 语言与音频设置
        self.front_lang_combobox: QComboBox = find_required_child(self.generate_from_csv_form,QComboBox, 'front_lang_combobox')
        self.front_subtitle_audio_engine_combobox: QComboBox = find_required_child(self.generate_from_csv_form,QComboBox, 'front_subtitle_audio_engine_combobox')
        self.back_lang_combobox: QComboBox = find_required_child(self.generate_from_csv_form,QComboBox, 'back_lang_combobox')
        self.back_subtitle_audio_engine_combobox: QComboBox = find_required_child(self.generate_from_csv_form,QComboBox, 'back_subtitle_audio_engine_combobox')

        
        # 选项设置
        self.front_ruby_checkbox: QCheckBox = find_required_child(self.generate_from_csv_form,QCheckBox, 'front_ruby_checkbox')
        self.back_ruby_checkbox: QCheckBox = find_required_child(self.generate_from_csv_form,QCheckBox, 'back_ruby_checkbox')
        self.cleanup_audio_checkbox: QCheckBox = find_required_child(self.generate_from_csv_form,QCheckBox, 'cleanup_audio_checkbox')
        self.overwrite_target_checkbox: QCheckBox = find_required_child(self.generate_from_csv_form,QCheckBox, 'overwrite_target_checkbox')

        # 操作按钮
        self.preview_button: QPushButton = find_required_child(self.generate_from_csv_form,QPushButton, 'preview_button')
        self.generate_button: QPushButton = find_required_child(self.generate_from_csv_form,QPushButton, 'generate_button')

        self.screenshot_source_combobox = find_required_child(self.generate_from_csv_form,QComboBox, "screenshot_source_combobox")
        
    def _init_widget_values(self):

        app_config = get_app_config()
        
        add_lang_to_combo_box(self.front_lang_combobox)
        add_lang_to_combo_box(self.back_lang_combobox)

        restore_lang_combobox(app_config.default_front_lang,self.front_lang_combobox)
        restore_lang_combobox(app_config.default_back_lang,self.back_lang_combobox)
    
        add_tts_engine_to_combobox(self.front_subtitle_audio_engine_combobox)
        add_tts_engine_to_combobox(self.back_subtitle_audio_engine_combobox)    
        
        engine_str=QCoreApplication.translate("generate_from_csv_form", "image search engines")
        add_image_creator_combobox(engine_str, self.screenshot_source_combobox)


    def _connect_signals(self):
        self.csv_file_button.clicked.connect(self.on_csv_file_button_clicked)
        self.output_folder_button.clicked.connect(self._on_output_folder_button_clicked)
        self.preview_button.clicked.connect(self._on_preview_button_clicked)
        self.generate_button.clicked.connect(self._on_generate_button_clicked)

        


    def on_csv_file_button_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self.generate_from_csv_form, QCoreApplication.translate("generate_from_csv_form","Select a csv file"),dir=get_app_config().last_media_folder, filter=QCoreApplication.translate("generate_from_csv_form","Multimudia files (*.csv)"))
        if file_name:
            self.csv_file_edit.setText(file_name)

            directory = os.path.dirname(file_name)
            base_name = os.path.splitext(os.path.basename(file_name))[0]

            self.anki_package_name_edit.setText(base_name)
            self.output_folder_edit.setText(os.path.join(directory, "anki_package"))

            save_last_media_folder(directory)

    def _on_output_folder_button_clicked(self):
        folder_name = QFileDialog.getExistingDirectory(self.generate_from_csv_form, QCoreApplication.translate("generate_from_csv_form","Select output folder"))
        if folder_name:
            self.output_folder_edit.setText(folder_name)

    def _create_anki_generator(self) -> BaseAnkiGenerator:
        sync_csv_config_from_ui(self.generate_from_csv_form, self.csv_config)

        self.csv_config.front_template=get_app_config().front_template
        self.csv_config.back_template=get_app_config().back_template
        self.csv_config.anki_style=get_app_config().anki_style

        anki_generaotr: BaseAnkiGenerator =  CsvAnkiGenerator(self.csv_config)
        return anki_generaotr

    def sync_configuration(self ) -> BaseAnkiConfig:
        
        sync_csv_config_from_ui(self.generate_from_csv_form, self.csv_config)

        return self.csv_config
     

    def get_anki_config(self) -> BaseAnkiConfig:
        return self.csv_config
    
    def check_condition(self, parent_widget: QWidget,anki_config :BaseAnkiConfig,progress:Progress) -> bool:

        if not os.path.exists(self.csv_config.csv_file):
            QMessageBox.critical(parent_widget, QCoreApplication.translate("base_form","error"), QCoreApplication.translate("generate_from_csv_form","Please select a CSV file encoded in UTF-8."))            
            return False
        

        return super().check_condition(parent_widget,anki_config,progress)
        
