import logging
import re

import pykakasi
from pypinyin import pinyin, Style
from korean_romanizer.romanizer import Romanizer

# 本地导入
from service.resource_manager import get_app_config


# Set up logging
logger = logging.getLogger(__name__)

class BaseRubyAppender():
    """
    An abstract base class for appending ruby characters (e.g., furigana) to text.
    """
    def __init__(self, *args, **kwargs):
        pass

    def append_ruby(self, text: str) -> str:        
        return text

class NoOpRubyAppender(BaseRubyAppender):
    """A RubyAppender that performs no operation and returns the text as is."""
    def append_ruby(self, text: str) -> str:
        return text

class JapaneseRubyAppender(BaseRubyAppender):
    """
    Appends furigana to Japanese text using fugashi.
    """
    def __init__(self):
        super().__init__()
        self.kakasi = None
        try:
            # Use the UniDic dictionary for better morphological analysis.
            self.kakasi = pykakasi.kakasi()
        except RuntimeError:
            logger.error(
                "Failed to initialize fugashi.Tagger. "
                "Make sure MeCab and a dictionary (e.g., unidic-lite) are installed. "
                "You can install them with: pip install fugashi[unidic-lite]"
            )

    def append_ruby(self, text: str) -> str:
        """
        Adds furigana to Japanese text using HTML <ruby> tags.
        It processes the text word by word, adding furigana only to words
        containing kanji where the reading differs from the surface form.

        Example:
            '日本語を勉強する' -> '<ruby><rb>日本語</rb><rt>にほんご</rt></ruby>を<ruby><rb>勉強</rb><rt>べんきょう</rt></ruby>する'
        """
        if not self.kakasi or not text:
            return text

        try:
            result = self.kakasi.convert(text)
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
            print(f"Warning: Failed to add Furigana to '{text}': {e}")
            # 可以添加日志记录或错误处理
            return text  # 返回原始文本作为回退

class ChineseRubyAppender(BaseRubyAppender):
    """
    Placeholder for a class that would add pinyin to Chinese text.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def append_ruby(self, text: str) -> str:
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
            print(f"Warning: Failed to add Pinyin to '{text}': {e}")
            return text # 发生错误时返回原文

class KoreanRubyAppender(BaseRubyAppender):
    def __init__(self):
        super().__init__()

    def append_ruby(self, text: str) -> str:
       
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
            print(f"Warning: Failed to add Romanization to '{text}': {e}")
           
            return text # 发生错误时返回原文

class RubyAppenderFactory:
    """
    一个单例工厂，用于创建和管理 BaseRubyAppender 实例。
    这确保了每种类型的 appender 只被创建一次并被复用。
    """
    _instance = None
    _APPENDER_MAP = {
        "ja": JapaneseRubyAppender,
        "ja-jp": JapaneseRubyAppender,
        "zh": ChineseRubyAppender,
        "zh-cn": ChineseRubyAppender,
        "zh-tw": ChineseRubyAppender,
        "zh-hans": ChineseRubyAppender,
        "zh-hant": ChineseRubyAppender, # Assuming same for traditional
        "ko": KoreanRubyAppender,
    }
    _noop_appender = NoOpRubyAppender()

    def __new__(cls):
        """确保单例模式。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_appender(self, lang_code: str) -> BaseRubyAppender:
       appender_class = self._APPENDER_MAP.get(lang_code.lower(), self._noop_appender)
       if appender_class == self._noop_appender:
           return appender_class
       return appender_class()
