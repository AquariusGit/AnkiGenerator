

from dataclasses import dataclass

@dataclass
class AnkiCard:
    front_text: str
    back_text: str
    front_text_ruby: str = ""
    back_text_ruby: str = ""
    
    front_audio: str = ""
    back_audio: str = ""
    screenshot: str = ""


    
    
    start_ms: int = 0  # 可选：音频/视频片段开始时间（毫秒）
    end_ms: int = 0    # 可选：音频/视频片段结束时间（毫秒）


        
