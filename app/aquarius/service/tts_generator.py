from gtts import gTTS
import edge_tts
from io import BytesIO
import asyncio
import os
from typing import Optional
from pydub import AudioSegment
import pyttsx3
import tempfile
import threading
import re

# 本地导入
from service.resource_manager import get_app_config

class BaseAudioGenerator:

    def __init__(self):
        self.exception_generator: Optional[BaseAudioGenerator]=None

    def generate(self, text,start_ms : int =0,end_ms :int =0) -> bytes:
        raise NotImplementedError
    
    def generate_to_file(self, lang_code:str,text,output_filename :str,start_ms : int =0,end_ms :int =0) :
        raise NotImplementedError
    
class NullAudioGenerator(BaseAudioGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, text,start_ms : int =0,end_ms :int =0) -> bytes:
        return b""

    def generate_to_file(self, lang_code:str,text,output_filename :str,start_ms : int =0,end_ms :int =0) :
        pass


class GttsAudioGenerator(BaseAudioGenerator):
    def __init__(self, slow :bool = False):
        super().__init__()
        self.slow = slow

    def generate(self, lang_code:str,text,start_ms,end_ms) -> bytes:
        tts = gTTS(text=text, lang=lang_code, slow=self.slow)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        return buffer.getvalue()

    def generate_to_file(self,lang_code:str, text, output_filename: str, start_ms: int = 0, end_ms: int = 0):
        
        new_lang_code = _find_suitable_lang_code(lang_code)
        tts = gTTS(text=text, lang=new_lang_code, slow=self.slow)
        tts.save(output_filename)

def _find_suitable_lang_code(code):
    """
    将完整语言代码转换为简写形式。

    参数:
    code (str): 完整的语言代码，如 'zh-CN' 或 'en-US'。

    返回:
    str: 转换后的简写语言代码，如 'zh' 或 'en'。
    """
    if '-' in code:
        # 如果包含 '-'，则移除 '-' 及其后面的部分
        return code.split('-')[0]
    else:
        # 如果不包含 '-'，则直接返回原始代码
        return code
        
    
class EdgeAudioGenerator(BaseAudioGenerator):

    _male_lang_to_voice = {
        "af": "af-ZA-WillemNeural",
        "am": "am-ET-AmehaNeural",
        "ar": "ar-SA-HamedNeural",
        "az": "az-AZ-BabekNeural",
        "bg": "bg-BG-BorislavNeural",
        "bn": "bn-IN-BashkarNeural",
        "bs": "bs-BA-GoranNeural",
        "ca": "ca-ES-EnricNeural",
        "cs": "cs-CZ-AntoninNeural",
        "cy": "cy-GB-AledNeural",
        "da": "da-DK-JeppeNeural",
        "de": "de-DE-ConradNeural",
        "el": "el-GR-NestorasNeural",
        "en": "en-US-GuyNeural",
        "en-AU": "en-AU-WilliamNeural",
        "en-CA": "en-CA-LiamNeural",
        "en-GB": "en-GB-RyanNeural",
        "en-US": "en-US-GuyNeural",
        "es-ES": "es-ES-AlvaroNeural",
        "et": "et-EE-KertNeural",
        "fa": "fa-IR-DilshadNeural",
        "fi": "fi-FI-HarriNeural",
        "fr-FR": "fr-FR-HenriNeural",
        "gu": "gu-IN-NiranjanNeural",
        "he": "he-IL-AvriNeural",
        "hi": "hi-IN-MadhurNeural",
        "hr": "hr-HR-SreckoNeural",
        "hu": "hu-HU-TamasNeural",
        "id": "id-ID-ArdiNeural",
        "it": "it-IT-DiegoNeural",
        "ja": "ja-JP-KeitaNeural",
        "jv": "jv-ID-DimasNeural",
        "km": "km-KH-PisethNeural",
        "kn": "kn-IN-GaganNeural",
        "ko": "ko-KR-InJoonNeural",
        "lo": "lo-LA-ChanthavongNeural",
        "lt": "lt-LT-LeonasNeural",
        "lv": "lv-LV-NilsNeural",
        "ml": "ml-IN-MidhunNeural",
        "mr": "mr-IN-ManoharNeural",
        "ms": "ms-MY-OsmanNeural",
        "my": "my-MM-ThihaNeural",
        "ne": "ne-NP-SagarNeural",
        "nl": "nl-NL-CoenNeural",
        "pl": "pl-PL-MarekNeural",
        "pt": "pt-BR-AntonioNeural",
        "pt-BR": "pt-BR-AntonioNeural",
        "pt-PT": "pt-PT-DuarteNeural",
        "ro": "ro-RO-EmilNeural",
        "ru": "ru-RU-DmitryNeural",
        "si": "si-LK-SameeraNeural",
        "sk": "sk-SK-LukasNeural",
        "sl": "sl-SI-RokNeural",
        "sr": "sr-RS-NicholasNeural",
        "sv": "sv-SE-MattiasNeural",
        "ta": "ta-IN-ValluvarNeural",
        "te": "te-IN-MohanNeural",
        "th": "th-TH-PremNeural",
        "tr": "tr-TR-AhmetNeural",
        "uk": "uk-UA-OstapNeural",
        "ur": "ur-PK-AsadNeural",
        "vi": "vi-VN-NamMinhNeural",
        "zh": "zh-CN-YunyangNeural",
        "zh-CN": "zh-CN-YunyangNeural",
        "zh-HK": "zh-HK-WanLungNeural",
        "zh-TW": "zh-TW-YunJheNeural"
    }

    _female_lang_to_voice = {
        "af": "af-ZA-AdriNeural",
        "am": "am-ET-MekdesNeural",
        "ar": "ar-SA-ZariyahNeural",
        "az": "az-AZ-BanuNeural",
        "bg": "bg-BG-KalinaNeural",
        "bn": "bn-IN-TanishaaNeural",
        "bs": "bs-BA-VesnaNeural",
        "ca": "ca-ES-JoanaNeural",
        "cs": "cs-CZ-VlastaNeural",
        "cy": "cy-GB-NiaNeural",
        "da": "da-DK-ChristelNeural",
        "de": "de-DE-KatjaNeural",
        "el": "el-GR-AthinaNeural",
        "en": "en-US-JennyNeural",
        "en-AU": "en-AU-NatashaNeural",
        "en-CA": "en-CA-ClaraNeural",
        "en-GB": "en-GB-SoniaNeural",
        "en-US": "en-US-JennyNeural",
        "es-ES": "es-ES-ElviraNeural",
        "et": "et-EE-AnuNeural",
        "fa": "fa-IR-FaridehNeural",
        "fi": "fi-FI-NooraNeural",
        "fr-FR": "fr-FR-DeniseNeural",
        "gu": "gu-IN-DhwaniNeural",
        "he": "he-IL-HilaNeural",
        "hi": "hi-IN-SwaraNeural",
        "hr": "hr-HR-GabrijelaNeural",
        "hu": "hu-HU-NoemiNeural",
        "id": "id-ID-GadisNeural",
        "it": "it-IT-ElsaNeural",
        "ja": "ja-JP-NanamiNeural",
        "jv": "jv-ID-SitiNeural",
        "km": "km-KH-SreymomNeural",
        "kn": "kn-IN-SapnaNeural",
        "ko": "ko-KR-SunHiNeural",
        "lo": "lo-LA-KeomanyNeural",
        "lt": "lt-LT-OnaNeural",
        "lv": "lv-LV-EveritaNeural",
        "ml": "ml-IN-MidhunNeural",
        "mr": "mr-IN-AarohiNeural",
        "ms": "ms-MY-YasminNeural",
        "my": "my-MM-NandarNeural",
        "ne": "ne-NP-SaritaNeural",
        "nl": "nl-NL-FennaNeural",
        "pl": "pl-PL-ZofiaNeural",
        "pt": "pt-BR-FranciscaNeural",
        "pt-BR": "pt-BR-FranciscaNeural",
        "pt-PT": "pt-PT-RaquelNeural",
        "ro": "ro-RO-AlinaNeural",
        "ru": "ru-RU-SvetlanaNeural",
        "si": "si-LK-TharukaNeural",
        "sk": "sk-SK-ViktoriaNeural",
        "sl": "sl-SI-PetraNeural",
        "sr": "sr-RS-SophieNeural",
        "sv": "sv-SE-SofieNeural",
        "ta": "ta-IN-PallaviNeural",
        "te": "te-IN-ShrutiNeural",
        "th": "th-TH-PremwadeeNeural",
        "tr": "tr-TR-AhsenNeural",
        "uk": "uk-UA-PolinaNeural",
        "ur": "ur-PK-UzmaNeural",
        "vi": "vi-VN-HoaiMyNeural",
        "zh": "zh-CN-XiaoxiaoNeural",
        "zh-CN": "zh-CN-XiaoxiaoNeural",
        "zh-HK": "zh-HK-HiuMaanNeural",
        "zh-TW": "zh-TW-HsiaoChenNeural"
        }

    def __init__(self, rate :int = 200):
        super().__init__()
        self.rate = rate

    async def generate(self, lang_code:str,text,start_ms,end_ms) -> bytes:

        
        # voice=self.find_voice(lang_code)
        # communicate = edge_tts.Communicate(text, voice)
        # buffer = BytesIO()

        voice = self.find_voice(lang_code)
    
        # 将文本按句号分割，并添加1秒停顿

        tts_text = self.create_ssml_text(text)

        communicate = edge_tts.Communicate(text=tts_text,voice=voice)
        buffer = BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio" and "data" in chunk:
                buffer.write(chunk["data"])

        return buffer.getvalue()

    def create_ssml_text(self, text):

        return text
        # sentences=[]

        # if re.search(r'\|{1,3}', text):
        #     sentences = re.split(r'\|{1,3}', text)
        #     sentences = [s.strip() for s in sentences if s.strip()]
        # else:        
        #     sentences = re.split(r'[。.?!？]', text)
        #     sentences = [s.strip() for s in sentences if s.strip()]
    
        # ssml_text = '<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.0" xml:lang="UTF-8">'
        
        # for i, sentence in enumerate(sentences):
        #     if len(sentence) >= 2:
        #         ssml_text += sentence
        #         if i < len(sentences) - 1:  # 不在最后一句后添加停顿
        #             ssml_text += '<break time="1000ms"/>'
        
        # ssml_text += '</speak>'
        # return ssml_text
    
    def generate_to_file(self,lang_code:str, text, output_filename: str, start_ms: int = 0, end_ms: int = 0):
        
        voice=self.find_voice(lang_code)    

        async def _generate_audio():    
            
            tts_text = self.create_ssml_text(text)
            communicate = edge_tts.Communicate(text=tts_text, voice=voice)
            await communicate.save(output_filename)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_generate_audio())

    def find_voice(self,lang_code: str) -> str:
        new_lang_code = _find_suitable_lang_code(lang_code)

        return self._male_lang_to_voice.get(new_lang_code, "en-US-JennyNeural")  # 默认使用英文语音



class Pyttsx3AudioGenerator(BaseAudioGenerator):
    def __init__(self, rate: int = 200, volume: float = 1.0):
        super().__init__()
        self.rate = rate
        self.volume = volume        

    def _run_engine_and_wait(self, engine):
        """在单独线程中运行 engine.runAndWait()"""
        engine.runAndWait()

    def generate(self, lang_code: str, text, start_ms: int = 0, end_ms: int = 0) -> bytes:
        # pyttsx3 直接生成音频到文件，然后读取
        engine = pyttsx3.init()
        
        # 根据slow参数设置语速
        actual_rate = self.rate
        
        engine.setProperty('rate', actual_rate)
        engine.setProperty('volume', self.volume)
        
        # 设置语言（如果支持）
        voices = engine.getProperty('voices')
        if lang_code and voices:
            suitable_voice = self._find_suitable_voice(lang_code, voices)
            if suitable_voice:
                engine.setProperty('voice', suitable_voice.id) # type: ignore
        
        # 使用临时文件存储音频
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_filename = tmp_file.name
        
        try:
            engine.save_to_file(text, temp_filename)
            # 使用线程执行 runAndWait() 避免阻塞
            thread = threading.Thread(target=self._run_engine_and_wait, args=(engine,))
            thread.start()
            thread.join()  # 等待线程完成
            
            # 读取音频文件
            audio_segment = AudioSegment.from_wav(temp_filename)
                        
            # 转换为MP3并返回字节
            buffer = BytesIO()
            audio_segment.export(buffer, format="mp3")
            return buffer.getvalue()
        finally:
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def generate_to_file(self, lang_code: str, text, output_filename: str, start_ms: int = 0, end_ms: int = 0):
        engine = pyttsx3.init()
        
        # 根据slow参数设置语速
        actual_rate = self.rate
        engine.setProperty('rate', actual_rate)
        engine.setProperty('volume', self.volume)
        
        # 设置语言（如果支持）
        voices = engine.getProperty('voices')
        if lang_code and voices:
            suitable_voice = self._find_suitable_voice(lang_code, voices)
            if suitable_voice:
                engine.setProperty('voice', suitable_voice.id) # type: ignore
        
        # 保存到目标文件
        engine.save_to_file(text, output_filename)
        # 使用线程执行 runAndWait() 避免阻塞
        thread = threading.Thread(target=self._run_engine_and_wait, args=(engine,))
        thread.start()
        thread.join()  # 等待线程完成


    # 需要在 Pyttsx3AudioGenerator 类中添加或修改以下方法
    def _find_suitable_voice(self, lang_code: str, voices) -> Optional[object]:
        """
        根据给定的语言代码查找最合适的语音。
        """
        if not lang_code or not voices:
            return None

        # 1. 标准化输入的语言代码，用于基础匹配
        base_lang_code = _find_suitable_lang_code(lang_code) # 复用已有函数

        # 2. 创建一个用于匹配的候选列表，优先级从高到低
        # 优先匹配完整代码 (e.g., zh-CN), 然后匹配基础代码 (e.g., zh)
        match_candidates = [lang_code.lower()]
        if base_lang_code != lang_code:
            match_candidates.append(base_lang_code.lower())

        # 3. 遍历语音列表进行匹配
        for candidate in match_candidates:
            for voice in voices:
                # 尝试匹配 voice.id (兼容性考虑)
                if candidate in voice.id.lower():
                    return voice

                # 尝试匹配 voice.languages (如果属性存在且可用)
                # 注意: pyttsx3 的 languages 属性在不同平台下可能不同，
                # 有时是列表，有时是字符串，需要处理
                if hasattr(voice, 'languages') and voice.languages:
                    # 假设它是一个可迭代对象或字符串
                    try:
                        if isinstance(voice.languages, str):
                            # 如果是字符串，直接比较（可能需要标准化）
                            normalized_voice_lang = _find_suitable_lang_code(voice.languages).lower()
                            if candidate == normalized_voice_lang or candidate in voice.languages.lower():
                                return voice
                        else:
                            # 假设是列表或其他可迭代对象
                            for v_lang in voice.languages:
                                normalized_v_lang = _find_suitable_lang_code(v_lang).lower()
                                if candidate == normalized_v_lang or candidate in v_lang.lower():
                                    return voice
                    except (TypeError, AttributeError):
                        # 如果访问或处理 languages 时出错，则跳过此匹配方式
                        pass
        return None # 如果没有找到匹配的语音

    

class FileAudioGenerator(BaseAudioGenerator):
    audio_segment: Optional[AudioSegment] = None  # 允许为 None

    def __init__(self, filename :str):
        super().__init__()
        self.filename = filename
        
    def generate(self, text,start_ms,end_ms) -> bytes:
        self.check_resource()
        segment : AudioSegment = self.audio_segment[start_ms:end_ms] # type: ignore
        buffer = BytesIO()
        segment.export(buffer, format="mp3")
        return buffer.getvalue()

    def check_resource(self):
        if self.audio_segment is None:
            with open(self.filename,"rb") as f:
                self.audio_segment = AudioSegment.from_file(f)
        
    
    def generate_to_file(self, lang_code: str, text, output_filename: str, start_ms: int = 0, end_ms: int = 0):
        self.check_resource()
        assert self.audio_segment is not None
        segment : AudioSegment  = self.audio_segment[start_ms:end_ms] # type: ignore
        segment.export(output_filename, format="mp3")



class AudioGeneratorFactory:
    """
    单例工厂类，用于根据配置获取适当的音频生成器实例
    """
    _instance = None
    _GENERATOR_MAP = {
        "gtts": GttsAudioGenerator(),
        "gtts-slow": GttsAudioGenerator(slow=True),
        "edge-tts": EdgeAudioGenerator(),
        "pyttsx3": Pyttsx3AudioGenerator(),
        "pyttsx3-slow": Pyttsx3AudioGenerator(rate=100)
    }
    _default_generator = EdgeAudioGenerator()  # 默认使用Edge TTS

    
    def __new__(cls):
        """确保单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_default_generator(self) ->BaseAudioGenerator:
        """获取默认的音频生成器"""
        return self._default_generator

    def set_default_generator(self, generator):
        """设置默认的音频生成器，支持传入类型字符串或生成器实例"""
        if isinstance(generator, str):
            self._default_generator = self._GENERATOR_MAP.get(generator, self._default_generator)
        elif isinstance(generator, BaseAudioGenerator):
            self._default_generator = generator
        else:
            raise ValueError("generator must be a string or an instance of BaseAudioGenerator")

    def get_generator(self, generator_type: str, slow: bool = False) -> Optional[BaseAudioGenerator]:   

        if generator_type == "none":
            return None

        audio_generator: Optional[BaseAudioGenerator] = None
        exception_audio_generator: BaseAudioGenerator = self._default_generator
        
        if slow:
            # 为slow选项选择合适的生成器
            slow_generator_type = generator_type + "-slow"

            if slow_generator_type in self._GENERATOR_MAP:
                audio_generator = self._GENERATOR_MAP.get(slow_generator_type)
            else:
                audio_generator = self._GENERATOR_MAP.get("gtts-slow")                
        else:   
            audio_generator = self._GENERATOR_MAP.get(generator_type)     

        # 确保 audio_generator 不为 None，若为 None 则使用默认生成器
        if audio_generator is None:
            audio_generator = self._default_generator

        # 特殊处理 edge-tts 的异常备选生成器
        if generator_type == "edge-tts":
            exception_audio_generator = self._GENERATOR_MAP.get("gtts", self._default_generator)

        # 安全设置 exception_generator
        audio_generator.exception_generator = exception_audio_generator # type: ignore

        return audio_generator  # type: ignore 