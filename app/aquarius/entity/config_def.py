from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class BaseAnkiConfig:
    """配置基类，包含所有配置类型的共同属性"""

    media_file: str = ""

    front_template: str = ""
    back_template: str = ""
    anki_style: str = ""
    
    anki_package_name: str = ""
    output_folder: str = ""
    
    # 音频相关设置
    front_subtitle_audio_engine: str = ""
    back_subtitle_audio_engine: str = ""

    front_lang:str = ""
    back_lang:str = ""
    
    # 注音选项
    front_ruby: bool = False
    back_ruby: bool = False
    
    # 清理选项
    # 清理选项
    cleanup_audio: bool = False
    cleanup_csv: bool = False
    cleanup_image: bool = False
    
    # 其他选项
    overwrite_target: bool = False

    screenshot_source: str = ""

@dataclass
class SubtitleConfig(BaseAnkiConfig):

    def __init__(self, other: Optional['SubtitleConfig'] = None):
        super().__init__()
        if other:
            # 复制所有属性
            self.__dict__.update(other.__dict__)

    
    front_subtitle_audio_slow: bool = False
    back_subtitle_audio_slow: bool = False

    """保存从字幕生成工具UI中提取的配置数据"""
    front_subtitle_file: str = ""
    back_subtitle_file: str = ""
    
    # 音频相关设置
    front_audio_offset: int = 0
    back_audio_offset: int = 0
    
    # 截图设置
    
    screenshot_period: int = 0 
    screenshot_quality: int = 2
    
    # 字幕处理选项
    subtitle_clean: bool = False
    front_ruby: bool = False
    back_ruby: bool = False
    
    
    
    # 时间范围设置
    time_range_start: str = ""
    time_range_end: str = ""
    
    
    # 其他选项
    overwrite_target: bool = False

@dataclass
class CsvConfig(BaseAnkiConfig):
    """保存从CSV生成工具UI中提取的配置数据"""
    csv_file: str = ""

@dataclass
class AppConfig:
    """保存应用程序通用配置数据"""
    default_front_lang: str = ""
    default_back_lang: str = ""
    default_tts: str = "gtts"
    front_template: str = "{{Question}}\n{{#Aupipdio_Question}}\n\t{{Audio_Question}}\n{{/Audio_Question}} \n\n{{#Description_Question}} \n\t<BR>{{Description_Question}}\n{{/Description_Question}}\n\n{{#Screenshot}} \n\t<BR>{{Screenshot}}\n{{/Screenshot}}\n"
    back_template: str = "{{Answer}}\n\n{{#Audio_Answer}}\n\t{{Audio_Answer}}\n{{/Audio_Answer}}\n\n{{#Description_Answer}}\n\t<BR>{{Description_Answer}}\n{{/Description_Answer}}\n\n{{#Screenshot}}\n\t<BR>{{Screenshot}}\n{{/Screenshot}}\n"
    anki_style: str = ".card {    font-family: arial;    font-size: 24px;    text-align: left;    color: black;    background-color: white;}"
    preview_html_template: str = "<!DOCTYPE html><html lang=\"zh\"><head><meta charset=\"UTF-8\"><title>Anki Preview</title>\n        <style>\n            body { font-family: sans-serif; background-color: #f0f0f0; padding: 20px; }\n            h1 { text-align: center; color: #333; }\n            .card-container { background-color: #fff; border: 1px solid #ccc; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }\n            .card-side h3 { color: #777; font-size: 1em; margin-top: 0; }\n            hr { border: 0; border-top: 1px solid #ddd; margin: 20px 0; }\n            {{style}}\n            .anki-back { display: block !important; }\n            ruby rt { font-size: 0.7em; }\n        </style></head><body><h1>Anki Preview</h1>{{cards_html}}</body></html>"
    language: str = ""

    last_media_folder : str = ""
    download_folder : str = ""

    sleep_interval : float = 2

    support_auto_caption: bool = False

    def get_sleep_interval(self) -> float:
        if self.sleep_interval is None:
            self.sleep_interval=2
            
        return self.sleep_interval
    
    
    