from PySide6.QtCore import  QObject,QLocale,Signal
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QMainWindow, 
                              QMenuBar, QTabWidget, QMessageBox, QPushButton, 
                              QComboBox, QLineEdit, QFileDialog,QCheckBox,QTextEdit)

from service.resource_manager import get_app_config, save_config
from ui.helper import add_lang_to_combo_box,restore_lang_combobox,add_tts_engine_to_combobox,find_required_child

from ui.qt_progress import Progress,QtProgress
import os

class ConfigurationFormController(QObject):

    # 添加语言改变信号
    language_changed = Signal(str)

    def __init__(self, configuration_form: QWidget, progress: Progress):
        super().__init__()
    
        self.configuration_form = configuration_form
        self.progress = progress
        
        self._fetch_children()
        self._init_language_combobox()        
        self._connect_signals()

        self.on_restore_button_clicked()

    def _connect_signals(self):
        self.save_pushbutton.clicked.connect(self.on_save_button_clicked)
        self.restore_pushbutton.clicked.connect(self.on_restore_button_clicked)

    def _fetch_children(self):
        """
        Fetches and assigns all the required child widgets from the config_form.
        """
        # 获取 QComboBox 控件
        self.default_front_lang_combobox = find_required_child(self.configuration_form,QComboBox, 'default_front_lang_combobox')
        self.default_back_lang_combobox = find_required_child(self.configuration_form,QComboBox, 'default_back_lang_combobox')
        self.default_tts_combobox = find_required_child(self.configuration_form,QComboBox, 'default_tts_combobox')
        self.sleep_interval_combobox=find_required_child(self.configuration_form,QComboBox, 'sleep_interval_combobox')
        
        self.sleep_interval_combobox.addItem("0.5s", 0.5)
        self.sleep_interval_combobox.addItem("1.0s", 1)
        self.sleep_interval_combobox.addItem("1.5s", 1.5)
        self.sleep_interval_combobox.addItem("2.0s", 2)
        self.sleep_interval_combobox.addItem("2.5s", 2.5)
        self.sleep_interval_combobox.addItem("3.0s", 3)
        self.sleep_interval_combobox.addItem("3.5s", 3.5)
        self.sleep_interval_combobox.addItem("4.0s", 4)
        self.sleep_interval_combobox.addItem("4.5s", 4.5)
        self.sleep_interval_combobox.addItem("5.0s", 5)

        # 获取 QTabWidget 和其内部的 QTextEdit 控件
        self.template_tab = find_required_child(self.configuration_form,QTabWidget, 'template_tab')

        # front_template_edit 在 front_template_tabpage 内部
        self.front_template_edit = find_required_child(self.configuration_form,QTextEdit, 'front_template_edit')

        # back_template_edit 在 back_template_tabpage 内部
        self.back_template_edit = find_required_child(self.configuration_form,QTextEdit, 'back_template_edit')

        # anki_style_tabpage 中的 textEdit
        self.anki_style_textedit = find_required_child(self.configuration_form,QTextEdit, 'anki_style_textedit')

        self.save_pushbutton = find_required_child(self.configuration_form,QPushButton, 'save_pushbutton')
        self.restore_pushbutton = find_required_child(self.configuration_form,QPushButton, 'restore_pushbutton')

        """设置语言选择器"""
        self.language_combobox = find_required_child(self.configuration_form,QComboBox, "language_combobox")
        

    def on_save_button_clicked(self):

        app_config = get_app_config()

        # 保存 QComboBox 的值到 app_config
        app_config.default_front_lang = self.default_front_lang_combobox.currentData()
        app_config.default_back_lang = self.default_back_lang_combobox.currentData()
        app_config.default_tts = self.default_tts_combobox.currentData()

        # 保存 QTextEdit 的内容到 app_config
        app_config.front_template = self.front_template_edit.toPlainText()
        app_config.back_template = self.back_template_edit.toPlainText()
        app_config.anki_style = self.anki_style_textedit.toPlainText()

        app_config.sleep_interval=self.sleep_interval_combobox.currentData()

        save_config(app_config)

        # 调用保存方法以持久化配置
    
            
    def on_language_changed(self, language_text):
        lang_code =self.language_combobox.currentData()
        app_config = get_app_config()
        app_config.language = lang_code

        save_config(app_config)
        
        # 发出语言改变信号
        self.language_changed.emit(lang_code)

        

    def on_restore_button_clicked(self):

        app_config = get_app_config()

        # 从 app_config 加载数据并更新到 UI 控件

        restore_lang_combobox(app_config.default_front_lang,self.default_front_lang_combobox)
        restore_lang_combobox(app_config.default_back_lang,self.default_back_lang_combobox)

        self.default_tts_combobox.setCurrentIndex(self.default_tts_combobox.findData(app_config.default_tts))

        sleep_interval = "{:.1f}s".format(app_config.get_sleep_interval())
        self.sleep_interval_combobox.setCurrentText(sleep_interval)
        
        self.front_template_edit.setPlainText(app_config.front_template)
        self.back_template_edit.setPlainText(app_config.back_template)
        self.anki_style_textedit.setPlainText(app_config.anki_style)

    def _init_language_combobox(self):
        add_lang_to_combo_box(self.default_front_lang_combobox)
        add_lang_to_combo_box(self.default_back_lang_combobox)
        add_tts_engine_to_combobox(self.default_tts_combobox)

        # 初始化语言选择器
        self._populate_language_combobox()
    
    def _populate_language_combobox(self):
        """
        遍历translations目录下的所有*.qm文件，根据文件名查询相应的语言，
        并以友好名称加入self.language_combobox
        """
        # 获取程序运行目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 假设代码在ui目录下
        translations_dir = os.path.join(base_dir, "translations")
        
        # 如果translations目录存在
        if os.path.exists(translations_dir) and os.path.isdir(translations_dir):
            # 遍历目录中的所有.qm文件
            for filename in os.listdir(translations_dir):
                if filename.endswith(".qm"):
                    # 提取语言代码（假设文件名格式为 app_zh.qm 或 app_en.qm）
                    lang_code = filename.split(".")[0]
                    
                    # 获取语言的友好名称
                    locale = QLocale(lang_code)
                    language_name = locale.nativeLanguageName()
                    
                    # 添加到language_combobox
                    self.language_combobox.addItem(language_name, lang_code)
    
        app_config=get_app_config()
        self.language_combobox.setCurrentIndex(self.language_combobox.findData(app_config.language))

        self.language_combobox.currentTextChanged.connect(self.on_language_changed)
            
        