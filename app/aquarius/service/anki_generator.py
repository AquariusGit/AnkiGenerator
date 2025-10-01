import requests
import re
import csv
import os
import random
import time
import subprocess
from typing import Tuple, Optional
from abc import ABC, abstractmethod

import webvtt
import pysrt
import json
from PIL import Image
from io import BytesIO
import bs4

import uuid
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

from PySide6.QtCore import QCoreApplication

# 本地导入
from entity.config_def import BaseAnkiConfig, SubtitleConfig, CsvConfig
from entity.anki_card import AnkiCard
from service.progress import Progress
from service.tts_generator import BaseAudioGenerator
from util.ruby import RubyAppenderFactory
import genanki

from service.resource_manager import is_not_blank,is_blank,get_app_config


from service.image_generator import BaseImageCreator, FfmpegImageCreator, ImageCreatorFactory



def simple_sanitize(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)


class BaseAnkiGenerator(ABC):

    def __init__(self,anki_config: BaseAnkiConfig):
        self.anki_config = anki_config

    def generate(self,  front_tts_audio_generator: Optional[BaseAudioGenerator],back_tts_audio_generator: Optional[BaseAudioGenerator] ,image_creator: Optional[BaseImageCreator] , progress: Progress) :
        
        try: 
            cards_data : list[AnkiCard]=self._generate_anki_cards(front_tts_audio_generator,back_tts_audio_generator,image_creator, progress)
            self._generate_anki_package(cards_data, front_tts_audio_generator, back_tts_audio_generator, image_creator, progress)
    
        except Exception as e:
            progress.error(str(e))
            raise
       
    @abstractmethod
    def _generate_anki_cards(self,  front_tts_audio_generator: Optional[BaseAudioGenerator],back_tts_audio_generator: Optional[BaseAudioGenerator]  ,image_creator: Optional[BaseImageCreator],progress: Progress) ->list[AnkiCard] :
        raise NotImplementedError

    def generate_anki_cards(self,  front_tts_audio_generator: Optional[BaseAudioGenerator],back_tts_audio_generator: Optional[BaseAudioGenerator]  ,image_creator: Optional[BaseImageCreator],progress: Progress) ->list[AnkiCard] :
        anki_cards :list[AnkiCard]= self._generate_anki_cards(front_tts_audio_generator,back_tts_audio_generator,image_creator, progress)
        self._update_anki_cards(anki_cards,front_tts_audio_generator, back_tts_audio_generator, image_creator, progress)

        return anki_cards

    def is_file_exist(self,filename:str)->bool:
        if is_blank(filename):
            return False
        
        full_file_path = os.path.join(self.anki_config.output_folder,filename)
        result:bool = os.path.exists(full_file_path)

        print(str(result) +"  "+full_file_path)
        return result
    
    def _generate_anki_package(self,  cards_data : list,front_tts_audio_generator: Optional[BaseAudioGenerator],back_tts_audio_generator: Optional[BaseAudioGenerator]  ,image_creator: Optional[BaseImageCreator],progress: Progress) :
        
        media_files_to_cleanup, screenshot_files_to_cleanup = self._update_anki_cards(cards_data, front_tts_audio_generator, back_tts_audio_generator, image_creator, progress)
        
        deck  , model  =self.create_new_deck(front_tts_audio_generator,back_tts_audio_generator,image_creator) 

        anki_card:AnkiCard

        for anki_card in cards_data:
            front_text_ruby = anki_card.front_text_ruby
            back_text_ruby = anki_card.back_text_ruby

            fields=[front_text_ruby, back_text_ruby]

            fields.append(anki_card.front_audio)
            fields.append(anki_card.back_audio)
            fields.append(anki_card.screenshot)
            
            note = genanki.Note(model=model,fields=fields)
           
            deck.add_note(note)

        package = genanki.Package(deck)
        package.media_files = media_files_to_cleanup + screenshot_files_to_cleanup    

        # 将字段数据写入同名CSV文件
        csv_file_path = self._write_csv_file(cards_data, model)

        file_name=simple_sanitize(self.anki_config.anki_package_name)
        output_file = os.path.join(self.anki_config.output_folder, f"{file_name}.apkg")
        
        try:
            package.write_to_file(output_file)            
        except Exception as e:
            error_text=QCoreApplication.translate("generator", "There was error {error} while generating the file : {file}.").format(error=str(e),file=os.path.abspath(output_file))
            progress.error(error_text)
            raise

        self.clear_files(media_files_to_cleanup, screenshot_files_to_cleanup,csv_file_path,progress=progress)

    def need_write_csv_file(self) -> bool:
        return False

    def _write_csv_file(self, cards_data, model) ->str:
        if not self.need_write_csv_file():
            return ""

        csv_file_path = os.path.join(self.anki_config.output_folder, f"{self.anki_config.anki_package_name}.csv")
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            # 写入表头
            header = [field['name'] for field in model.fields]
            csv_writer.writerow(header)

            # 写入每张卡片的数据
            for anki_card in cards_data:
                csv_writer.writerow([anki_card.front_text_ruby, anki_card.back_text_ruby, anki_card.front_audio, anki_card.back_audio, anki_card.screenshot])
        return csv_file_path

    def _retry_generate_audio_to_file(self, tts_audio_generator, lang_code, text, audio_path, start_ms, end_ms):
        exception_tts_audio_generator  = tts_audio_generator.exception_generator
        max_attempts = 2

        for attempt in range(max_attempts):
            try:
                tts_audio_generator.generate_to_file(lang_code, text, audio_path, start_ms, end_ms)
                # 在这里暂停指定秒数
                time.sleep(get_app_config().get_sleep_interval())
                return  # 成功则退出
            except Exception as e:        
                if attempt < max_attempts - 1:
                    print(f"第 {attempt + 1} 次尝试失败，正在重试... 错误: {e}")
                    # 在这里暂停指定秒数
                    time.sleep(get_app_config().get_sleep_interval())
                    
                else:
                    print(f"主TTS生成器失败，尝试使用异常处理生成器... 错误: {e}  "+tts_audio_generator.__class__.__name__)

        # 主生成器失败后，使用异常生成器再试两次
        for attempt in range(max_attempts):
            try:
                exception_tts_audio_generator.generate_to_file(lang_code, text, audio_path, start_ms, end_ms)

                # 在这里暂停指定秒数
                time.sleep(get_app_config().get_sleep_interval())
                return  # 成功则退出
            except Exception as e:
                if attempt < max_attempts - 1:
                    
                    print(f"异常TTS生成器第 {attempt + 1} 次尝试失败，正在重试... 错误: {e}  "+exception_tts_audio_generator.__class__.__name__)

                    # 在这里暂停指定秒数
                    time.sleep(get_app_config().get_sleep_interval())
                else:
                    error_text=QCoreApplication.translate("generator", "There was error {error} while generating the audio of : {front_text}.").format(error=str(e),front_text=text)
                    raise RuntimeError(error_text) from e
    
    def _update_anki_cards(self, cards_data, front_tts_audio_generator, back_tts_audio_generator, image_creator:Optional[BaseImageCreator], progress:Progress):
        front_lang=self.anki_config.front_lang
        back_lang=self.anki_config.back_lang     

        total_cards = len(cards_data)
        last_progress_update = -1

        factory = RubyAppenderFactory()
        front_ruby_appender = factory.get_appender(front_lang)
        back_ruby_appender = factory.get_appender(back_lang)
       
        media_files_to_cleanup = []
        screenshot_files_to_cleanup = []

        anki_card: AnkiCard         

        for i, anki_card in enumerate(cards_data):
            current_progress = (i / total_cards) * 100
            if current_progress - last_progress_update >= 1 or i == total_cards - 1:
                current_progress_value=int(current_progress)

                progress_info=QCoreApplication.translate("generator", "Processing cards ： {current_cards}/{total_cards}")
                progress_info=progress_info.format(current_cards=i+1, total_cards=total_cards)
                progress.update_info(current_progress_value,progress_info)                
                
                last_progress_update = current_progress

            front_text = anki_card.front_text
            back_text = anki_card.back_text
            front_text_ruby=front_text
            back_text_ruby=back_text

            # 将'。\n'和'？\n',替换为'\n' ，是因为不知道为什么日语加注音符时，会在换行符后面多加一个"。"或"？"
            if self.anki_config.front_ruby:
                front_text_ruby = front_ruby_appender.append_ruby(front_text)
                front_text_ruby = front_text_ruby.replace('\n。', '\n')   
                front_text_ruby = front_text_ruby.replace('\n？', '\n')            
                front_text_ruby = front_text_ruby.replace('\n', '<P>')   

            if self.anki_config.back_ruby:
                back_text_ruby = back_ruby_appender.append_ruby(back_text)
                back_text_ruby = back_text_ruby.replace('\n。', '\n')
                back_text_ruby = back_text_ruby.replace('\n？', '\n')
                back_text_ruby = back_text_ruby.replace('\n', '<P>')

            anki_card.front_text_ruby = front_text_ruby
            anki_card.back_text_ruby = back_text_ruby

            start_ms = anki_card.start_ms
            end_ms = anki_card.end_ms

            
            if front_tts_audio_generator is not None:
                front_audio = f"segment_front_{i+1:06d}.mp3"
                front_audio_path = os.path.join(self.anki_config.output_folder, front_audio)
                self._retry_generate_audio_to_file(front_tts_audio_generator, front_lang, front_text, front_audio_path,start_ms,end_ms)
                
                
                if os.path.exists(front_audio_path):
                    media_files_to_cleanup.append(front_audio_path)
                    anki_card.front_audio = f"[sound:{front_audio}]"
                

            if back_tts_audio_generator is not None:
                back_audio = f"segment_back_{i+1:06d}.mp3"
                back_audio_path = os.path.join(self.anki_config.output_folder, back_audio)
                self._retry_generate_audio_to_file(back_tts_audio_generator, back_lang, back_text, back_audio_path, start_ms, end_ms)
                
                if os.path.exists(front_audio_path):
                    media_files_to_cleanup.append(back_audio_path)
                    anki_card.back_audio = f"[sound:{back_audio}]"
            
            if image_creator is not None:
                screenshot = f"screenshot_{i+1:06d}.jpg"
                screenshot_path = os.path.join(self.anki_config.output_folder, screenshot)

                self._retry_generate_screenshot_to_file(image_creator, progress, screenshot_files_to_cleanup, anki_card, front_text, start_ms, screenshot, screenshot_path)         
                if os.path.exists(screenshot_path):
                    screenshot_files_to_cleanup.append(screenshot_path)
                    anki_card.screenshot=f'<img src="{screenshot}">'          
        
        return media_files_to_cleanup,screenshot_files_to_cleanup

    def _retry_generate_screenshot_to_file(self, image_creator, progress, screenshot_files_to_cleanup, anki_card:AnkiCard, front_text, start_ms, screenshot, screenshot_path):
        
        try:            
            image_creator.create_images(front_text, screenshot_path, progress,start_ms)  
            time.sleep(get_app_config().get_sleep_interval())              
        except Exception as e:
            error_text = QCoreApplication.translate("generator", "Error while create image for {front_text}: {error}").format(text=front_text, error=str(e))
            progress.error(error_text)
        
    def clear_files(self, media_files_to_cleanup, screenshot_files_to_cleanup,csv_file_path, progress: Progress):
    
        if self.anki_config.cleanup_csv:
            delete_file(csv_file_path,progress)

        if self.anki_config.cleanup_audio:            
            for file in media_files_to_cleanup:
                delete_file(file,progress)
                

        if self.anki_config.cleanup_image:
            for file in screenshot_files_to_cleanup:
                delete_file(file,progress)            
        

    def create_new_deck(self, front_tts_audio_generator: Optional[BaseAudioGenerator], back_tts_audio_generator: Optional[BaseAudioGenerator] ,image_creator: Optional[BaseImageCreator] ) -> Tuple[genanki.Deck, genanki.Model]:
        deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), self.anki_config.anki_package_name)
        
        fields=[
                {'name': 'Question'},
                {'name': 'Answer'}
            ]
        
        # fixme

        #if front_tts_audio_generator is not None:
        fields.append({'name': 'Audio_Question'})

        #if back_tts_audio_generator is not None:
        fields.append({'name': 'Audio_Answer'})

        #if image_creator is not None:
        fields.append({'name': 'Screenshot'})

        anki_model_name=QCoreApplication.translate("generator", "Anki Card Generator")     
        anki_card_name =QCoreApplication.translate("generator", "Bilingual Learning Card")     
        
        model = genanki.Model(
            random.randrange(1 << 30, 1 << 31),
            anki_model_name,
            fields,
            templates=[
                {
                    'name': anki_card_name,
                    'qfmt': self.anki_config.front_template,
                    'afmt': self.anki_config.back_template,
                },
            ],
            css=self.anki_config.anki_style
        )

        return deck,model


class SubtitleAnkiGenerator(BaseAnkiGenerator):
    def __init__(self, subtitle_config: SubtitleConfig):
        super().__init__(subtitle_config)
        self._subtitle_config = subtitle_config
    
    def _generate_anki_cards(self, front_tts_audio_generator: BaseAudioGenerator | None, back_tts_audio_generator: BaseAudioGenerator | None, image_creator: BaseImageCreator | None, progress: Progress) -> list[AnkiCard]:
        # 根据文件扩展名选择解析方式
        front_extension = os.path.splitext(self._subtitle_config.front_subtitle_file)[1].lower()
        back_extension = os.path.splitext(self._subtitle_config.back_subtitle_file)[1].lower()
        
        # 解析前端和后端字幕文件
        if front_extension == '.srt':
            front_sub = pysrt.open(self._subtitle_config.front_subtitle_file)
            # 转换为统一格式以便后续处理
            front_items = [(item.start.ordinal, item.end.ordinal, item.text) for item in front_sub]
        elif front_extension == '.vtt':
            front_vtt = webvtt.read(self._subtitle_config.front_subtitle_file)
            front_items = []
            for caption in front_vtt:
                start_ms = self._timestamp_to_milliseconds(caption.start)
                end_ms = self._timestamp_to_milliseconds(caption.end)
                front_items.append((start_ms, end_ms, caption.text))
        else:
            raise ValueError(f"Unsupported subtitle format for front subtitle: {front_extension}")
            
        if back_extension == '.srt':
            back_sub = pysrt.open(self._subtitle_config.back_subtitle_file)
            # 转换为统一格式以便后续处理
            back_items = [(item.start.ordinal, item.end.ordinal, item.text) for item in back_sub]
        elif back_extension == '.vtt':
            back_vtt = webvtt.read(self._subtitle_config.back_subtitle_file)
            back_items = []
            for caption in back_vtt:
                start_ms = self._timestamp_to_milliseconds(caption.start)
                end_ms = self._timestamp_to_milliseconds(caption.end)
                back_items.append((start_ms, end_ms, caption.text))
        else:
            raise ValueError(f"Unsupported subtitle format for back subtitle: {back_extension}")

        # 确保两个字幕文件数量相同
        if len(front_items) != len(back_items):
            error_text=QCoreApplication.translate("generator", "The number of subtitles does not match")
            raise ValueError(error_text)
        
        # 转换时间范围字符串为毫秒
        time_range_start_ms = time_str_to_milliseconds(self._subtitle_config.time_range_start)
        time_range_end_ms = time_str_to_milliseconds(self._subtitle_config.time_range_end)
            
        # 用于去除[]内的内容，如[掌声][音乐]等
        bracket_pattern = re.compile(r'\[.*?\]')
        
        cards_data = []
        for (front_start, front_end, front_text), (back_start, back_end, back_text) in zip(front_items, back_items):

            # 增加时间范围检查
            start_time_ms = front_start
            
            # 如果设置了开始时间且当前字幕开始时间早于设置的开始时间，则跳过
            if (time_range_start_ms is not None and 
                start_time_ms <= time_range_start_ms):
                continue
                
            # 如果设置了结束时间且当前字幕开始时间晚于设置的结束时间，则跳过
            if (time_range_end_ms is not None and 
                start_time_ms >= time_range_end_ms):
                continue

            # 去除[]内的内容并清理文本
            front_text = bracket_pattern.sub('', front_text).strip()
            back_text = bracket_pattern.sub('', back_text).strip()

            if is_blank(front_text) or is_blank(back_text):
                continue
        
            anki_card = AnkiCard(front_text, back_text)
            anki_card.start_ms = front_start + self._subtitle_config.front_audio_offset
            anki_card.end_ms = front_end + self._subtitle_config.front_audio_offset

            cards_data.append(anki_card)
        
        self._update_anki_cards(cards_data, front_tts_audio_generator, back_tts_audio_generator, image_creator, progress)
        return cards_data
    
    def need_write_csv_file(self) -> bool:
        return True
    
    def _timestamp_to_milliseconds(self, timestamp: str) -> int:
        """
        将 WebVTT 时间戳转换为毫秒
        WebVTT 时间戳格式: HH:MM:SS.mmm
        """
        hours, minutes, seconds = timestamp.split(':')
        seconds, milliseconds = seconds.split('.')
        total_ms = (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int(milliseconds)
        return total_ms


class CsvAnkiGenerator(BaseAnkiGenerator):
    def __init__(self, csv_config: CsvConfig):
        super().__init__(csv_config)
        self._csv_config = csv_config
    
    def _generate_anki_cards(self, front_tts_audio_generator: BaseAudioGenerator | None, back_tts_audio_generator: BaseAudioGenerator | None, image_creator: BaseImageCreator | None, progress: Progress) -> list[AnkiCard]:
        csv_file = self._csv_config.csv_file
        cards_data = []

        try:
            # 从CSV读取数据
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                
                for row in reader:
                    if len(row) >= 2: # Ensure row has at least two columns for front and back text
                        front_text = row[0].strip()
                        back_text = row[1].strip()
        
                        if front_text and back_text:  # 确保两个字段都不为空
                            anki_card = AnkiCard(front_text, back_text)
                            cards_data.append(anki_card)
        except Exception as e:
            progress.info(QCoreApplication.translate("generator", "Error while parsing csv: {error}.\nPlease make sure the format is right and encoded in UTF-8").format(error=str(e)))
            raise e

        return cards_data


def time_str_to_milliseconds(time_str):
    """
    将 hh:mm:ss 格式的时间字符串转换为毫秒
    """
    if time_str is None:
        return None
    
    time_str=time_str.strip()
    if time_str == '00' or time_str == '00:00' or time_str == '00:00:00':
        return None
    
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            return None
            
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        
        total_milliseconds = (hours * 3600 + minutes * 60 + seconds) * 1000
        return int(total_milliseconds)
    except (ValueError, AttributeError):
        return None


def delete_file(file_path,progress: Progress):
    try:
        if (file_path is not None ) and (file_path != "") and os.path.exists(file_path) :
            os.remove(file_path)
    except FileNotFoundError:
        error_text=QCoreApplication.translate("generator", "The file of {file_path} was not found.").format(file_path=file_path)
        progress.warning(error_text)            
    except PermissionError:
        error_text=QCoreApplication.translate("generator", "The file deleting of {file_path} was not allowed.").format(file_path=file_path)
        progress.warning(error_text)            
    except Exception as e:
        error_text=QCoreApplication.translate("generator", "The file of {file_path} was not deleted.").format(file_path=file_path)
        progress.warning(error_text)            
