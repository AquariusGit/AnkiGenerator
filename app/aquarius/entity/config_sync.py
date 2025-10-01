from PySide6.QtWidgets import QWidget, QMessageBox
from entity.config_def import SubtitleConfig, CsvConfig, AppConfig,BaseAnkiConfig


def sync_subtitle_config_from_ui(ui_form: QWidget ,subtitle_config: SubtitleConfig):
    
    sync_anki_config_from_ui(ui_form, subtitle_config)
    
    # 文件路径相关配置
    subtitle_config.media_file = ui_form.media_file_edit.text() # type: ignore
    subtitle_config.front_subtitle_file = ui_form.front_subtitle_file_edit.text() # type: ignore
    subtitle_config.back_subtitle_file = ui_form.back_subtitle_file_edit.text() # type: ignore
    
    
    # 音频相关设置
    subtitle_config.front_audio_offset = ui_form.front_subtitle_audio_offset_spinbox.value() # type: ignore
    subtitle_config.front_subtitle_audio_slow=ui_form.front_subtitle_audio_slow_checkbox.isChecked() # type: ignore
    
    subtitle_config.back_audio_offset = ui_form.back_subtitle_audio_offset_spinbox.value() # type: ignore
    subtitle_config.back_subtitle_audio_slow=ui_form.back_subtitle_audio_slow_checkbox.isChecked()     # type: ignore
    
    # 截图设置
    subtitle_config.screenshot_source=ui_form.screenshot_source_combobox.currentData() # type: ignore
    subtitle_config.screenshot_period = ui_form.screenshot_period_combobox.currentIndex() # type: ignore
    subtitle_config.screenshot_quality = ui_form.screenshot_quality_combobox.currentIndex() # type: ignore
    
    # 字幕处理选项
    subtitle_config.subtitle_clean = ui_form.subtitle_clean_checkbox.isChecked() # type: ignore
        
    # 清理选项
    subtitle_config.cleanup_csv = ui_form.cleanup_csv_checkbox.isChecked() # type: ignore
    subtitle_config.cleanup_image = ui_form.cleanup_image_checkbox.isChecked() # type: ignore
    
    # 时间范围设置
    subtitle_config.time_range_start = ui_form.time_range_start_timeedit.time().toString("hh:mm:ss") # type: ignore
    subtitle_config.time_range_end = ui_form.time_range_end_timeedit.time().toString("hh:mm:ss") # type: ignore
    
    
    return subtitle_config

def sync_anki_config_from_ui(ui_form: QWidget, anki_config: BaseAnkiConfig):
    # 文件路径相关配置
    
    anki_config.anki_package_name = ui_form.anki_package_name_edit.text() # type: ignore
    anki_config.output_folder = ui_form.output_folder_edit.text() # type: ignore

    # 音频相关设置
    anki_config.front_subtitle_audio_engine = ui_form.front_subtitle_audio_engine_combobox.currentData() # type: ignore
    anki_config.front_lang = ui_form.front_lang_combobox.currentData() # type: ignore
    
    anki_config.back_subtitle_audio_engine = ui_form.back_subtitle_audio_engine_combobox.currentData() # type: ignore
    anki_config.back_lang = ui_form.back_lang_combobox.currentData() # type: ignore

    # 注音选项
    anki_config.front_ruby = ui_form.front_ruby_checkbox.isChecked() # type: ignore
    anki_config.back_ruby = ui_form.back_ruby_checkbox.isChecked() # type: ignore

    # 清理选项
    anki_config.cleanup_audio = ui_form.cleanup_audio_checkbox.isChecked() # type: ignore

    # 其他选项
    anki_config.overwrite_target = ui_form.overwrite_target_checkbox.isChecked() # type: ignore

    anki_config.screenshot_source=ui_form.screenshot_source_combobox.currentData() # type: ignore


def sync_csv_config_from_ui(ui_form: QWidget,csv_config: CsvConfig):
    """从generate_from_csv.ui表单同步数据到CsvConfig对象"""
        
    csv_config.csv_file = ui_form.csv_file_edit.text() # type: ignore
    
    sync_anki_config_from_ui(ui_form, csv_config)    
    

def sync_app_config(ui_form: QWidget, app_config: AppConfig):
    """从UI表单同步配置数据"""
    
    
    # 同步语言选择
    app_config.default_front_lang = ui_form.default_front_lang_combobox.currentText() # type: ignore
    app_config.default_back_lang = ui_form.default_back_lang_combobox.currentText() # type: ignore

    app_config.front_template = ui_form.front_template_edit.toPlainText() # type: ignore
    app_config.back_template = ui_form.back_template_edit.toPlainText() # type: ignore
    app_config.anki_style = ui_form.textEdit.toPlainText() # type: ignore
               
