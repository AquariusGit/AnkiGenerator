import sys
import os
import tempfile
from typing import Optional
from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import QObject, Signal, QThread, QUrl
from PySide6.QtGui import QDesktopServices

# 本地导入
from util.localization import get_available_display_languages
from service.resource_manager import get_app_config, save_config, add_temp_file, save_download_folder, save_last_media_folder,is_blank
from entity.anki_card import AnkiCard
from ui.qt_progress import Progress, QtProgress
from ui.helper import is_media_file_tts
from service.anki_generator import BaseAnkiGenerator, SubtitleAnkiGenerator
from service.tts_generator import AudioGeneratorFactory, BaseAudioGenerator, FileAudioGenerator
from service.image_generator import BaseImageCreator, FfmpegImageCreator,ImageCreatorFactory
from service.worker import GenerationWorker
from entity.config_def import SubtitleConfig, BaseAnkiConfig
from PySide6.QtCore import QCoreApplication
from entity.config_def import AppConfig

def create_anki_cards(anki_generaotr,progress: Progress):

    priview_html_template = """<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><title>Anki Cards Preview</title>
        <style>
            body { font-family: sans-serif; background-color: #f0f0f0; padding: 20px; }
            h1 { text-align: center; color: #333; }
            .card-container { background-color: #fff; border: 1px solid #ccc; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .card-side h3 { color: #777; font-size: 1em; margin-top: 0; }
            hr { border: 0; border-top: 1px solid #ddd; margin: 20px 0; }
            {{style}}
            .anki-back { display: block !important; }
            ruby rt { font-size: 0.7em; }
        </style></head><body><h1>Anki Cards Preview</h1>{{cards_html}}</body></html>"""
    
    anki_cards :list[AnkiCard] = anki_generaotr.generate_anki_cards(None,None,None, progress)
    cards_html:str=""

    app_config:AppConfig = get_app_config()

    front_template = "{{Question}}\n{{Audio_Question}}"
    back_template = "{{Answer}}\n{{Audio_Answer}}"
    style = app_config.anki_style
    preview_html_template = app_config.preview_html_template
    audio_placeholder_q = "<div style='color: #888; font-style: italic;'>⏩</div>"
    audio_placeholder_a = "<div style='color: #888; font-style: italic;'>⏩</div>"
    screenshot_placeholder = "<div style='color: #888; font-style: italic;'>🌇</div>"

    for i, card in enumerate(anki_cards):
        question = card.front_text_ruby
        answer = card.back_text_ruby

        front_html = front_template.replace("{{Question}}", card.front_text_ruby).replace("{{Audio_Question}}", audio_placeholder_q)
        back_html = back_template.replace("{{Answer}}", card.back_text_ruby).replace("{{Audio_Answer}}", audio_placeholder_a).replace("{{Screenshot}}", screenshot_placeholder)
        
        preview_card_title=QCoreApplication.translate("base_form","preview card title")+" "+str(i+1)
        preview_card_front=QCoreApplication.translate("base_form","preview card front")
        preview_card_back=QCoreApplication.translate("base_form","preview card back")
        
        html= f"""
            <div class="card-container">
                <h2>{preview_card_title}</h2>
                <div class="card-side"><h3>{("preview_card_front")}</h3><div class="card">{front_html}</div></div>
                <div class="card-side"><h3>{("preview_card_back")}</h3><div class="card anki-back">{back_html}</div></div>
            </div><hr>"""

        cards_html=cards_html+html
    
    app_config=get_app_config()

    if "{{cards_html}}" in app_config.preview_html_template:
        cards_html=app_config.preview_html_template.replace("{{cards_html}}",cards_html)
    else:
        cards_html=preview_html_template.replace("{{cards_html}}",cards_html)
    
    return cards_html

def show_html_preview_dialog(html_content):
    # 创建临时文件（不立即删除）
    try:
        # 创建临时 HTML 文件
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.html', encoding='utf-8') as tmpfile:
            tmpfile.write(html_content)
            tmpfile_path = tmpfile.name

        # 使用系统默认浏览器打开临时文件
        url = QUrl.fromLocalFile(tmpfile_path)
        add_temp_file(tmpfile_path)
        QDesktopServices.openUrl(url)
        

    except Exception as e:
        
        pass

class BaseFormController(QObject):

    def __init__(self, form_widget: QWidget, progress):
        super().__init__(form_widget)
        self.form_widget:QWidget = form_widget
        self.progress = progress
        self.worker: Optional[GenerationWorker] = None  # 保存worker引用

    def start_thread(self,anki_generaotr : BaseAnkiGenerator, parent_widget: QWidget, anki_config :BaseAnkiConfig,progress:Progress) :
        
        if self.worker is not None:  # 检查线程是否正在运行            
            QMessageBox.warning(parent_widget, QCoreApplication.translate("base_form","wait"), QCoreApplication.translate("base_form","Please wait for the current generation to finish."))
            return False  

        self.worker = self.create_generator_worker(anki_generaotr, anki_config, progress)

        if self.worker is not None:
            # 连接信号
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.on_worker_finished)
            
            # 启动线程
            self.worker.start()

    def create_generator_worker(self, anki_generaotr, anki_config:BaseAnkiConfig, progress) -> Optional[GenerationWorker]:

        if os.path.exists(anki_config.media_file) and is_media_file_tts(anki_config.front_subtitle_audio_engine):
            front_tts_audio_generator :  Optional[BaseAudioGenerator] =FileAudioGenerator(anki_config.media_file)
            front_tts_audio_generator.exception_generator=AudioGeneratorFactory().get_default_generator()
        else:
            front_tts_audio_generator: Optional[BaseAudioGenerator] =AudioGeneratorFactory().get_generator(anki_config.front_subtitle_audio_engine)
        
        if os.path.exists(anki_config.media_file) and is_media_file_tts(anki_config.back_subtitle_audio_engine):
            back_tts_audio_generator=FileAudioGenerator(anki_config.media_file)
            back_tts_audio_generator.exception_generator=AudioGeneratorFactory().get_default_generator()
        else:
            back_tts_audio_generator=AudioGeneratorFactory().get_generator(anki_config.back_subtitle_audio_engine)
        
        image_creator : Optional[BaseImageCreator]=None

        if  os.path.exists(anki_config.media_file) and anki_config.screenshot_source=="screenshot":
            image_creator = FfmpegImageCreator(anki_config.media_file)        
        else:
            image_creator=ImageCreatorFactory().get_image_creator(anki_config.screenshot_source)

        
        # 保存worker引用以防止被垃圾回收
        return GenerationWorker(anki_generaotr, front_tts_audio_generator, back_tts_audio_generator, image_creator, progress)
        
    def check_condition(self, parent_widget: QWidget,anki_config :BaseAnkiConfig,progress:Progress) -> bool:
        
        if is_blank(anki_config.anki_package_name):
            QMessageBox.critical(parent_widget, QCoreApplication.translate("base_form","error"), QCoreApplication.translate("base_form","Please specify a name of the anki package."))            
            return False            

        output_dir = anki_config.output_folder
        if not output_dir:
            QMessageBox.critical(parent_widget, QCoreApplication.translate("base_form","error"), QCoreApplication.translate("base_form","Please select an output folder"))            
            return False

        # 如果路径存在但不是目录，则报错
        if os.path.exists(output_dir) and not os.path.isdir(output_dir):
            error_text=QCoreApplication.translate("base_form","The output folder is not a directory")+": " + output_dir
            QMessageBox.critical(parent_widget, QCoreApplication.translate("base_form","error"), error_text)                        
            return False
        
        # 如果路径不存在，则创建它
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                error_text=QCoreApplication.translate("base_form","The output folder is not exist\n It was created.")+": " + output_dir
                progress.info(error_text)
            except Exception as e:
                error_text=QCoreApplication.translate("base_form","The output folder is not created.\nPlease check ")+": " + output_dir
                QMessageBox.critical(parent_widget, QCoreApplication.translate("base_form","error"), error_text)                    
                return False
        
        return True
    
    @abstractmethod
    def sync_configuration(self ) -> BaseAnkiConfig:
        pass        
    
    def _on_generate_button_clicked(self):
        anki_config:BaseAnkiConfig = self.sync_configuration()
        anki_generaotr = self._create_anki_generator()

        if not self.check_condition(self.form_widget,anki_config,self.progress):
            return False  

        self.start_thread(anki_generaotr,self.form_widget, anki_config,progress=self.progress)        
    
    def _on_preview_button_clicked(self):

        anki_config:BaseAnkiConfig = self.sync_configuration()

        if self.check_condition(self.form_widget,self.get_anki_config(),self.progress) == False: 
            return

        anki_generaotr = self._create_anki_generator()        
        
        cards_html = create_anki_cards(anki_generaotr,self.progress)            
        show_html_preview_dialog(cards_html)

        self.progress.update_progress(0)

    def on_worker_finished(self):
        self.worker = None  # 清除引用

        self.progress.update_progress(0)

        # 添加任务完成提示框
        reply =QMessageBox.question(
            self.form_widget, 
            QCoreApplication.translate("base_form", "Task completed"), 
            QCoreApplication.translate("base_form", "Task of generating anki was completed successfully!Will you open the anki folder now"), 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        # 如果用户选择是，则打开输出目录
        if reply == QMessageBox.StandardButton.Yes:
            anki_config=self.get_anki_config()
            output_folder = anki_config.output_folder
            if output_folder and os.path.exists(output_folder):
                url = QUrl.fromLocalFile(output_folder)
                QDesktopServices.openUrl(url)


    def _create_anki_generator(self) -> BaseAnkiGenerator:
        raise NotImplementedError
    
    @abstractmethod
    def get_anki_config(self) -> BaseAnkiConfig:
        pass        

# ... rest of the file remains the same



    

    