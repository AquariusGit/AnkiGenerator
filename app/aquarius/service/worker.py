
from PySide6.QtCore import QThread

# 本地导入
from service.progress import Progress
from service.anki_generator import BaseAnkiGenerator
from service.tts_generator import BaseAudioGenerator
from service.image_generator import BaseImageCreator
from typing import Optional

class GenerationWorker(QThread):
    # 移除 finished 信号，因为 QThread 已经有 finished 信号
    # finished = Signal()
    
    def __init__(self, anki_generator : Optional[BaseAnkiGenerator], front_tts_audio_generator:  Optional[BaseAudioGenerator], back_tts_audio_generator:  Optional[BaseAudioGenerator], image_creator: Optional[BaseImageCreator], progress: Optional[Progress] = None    ):
        super().__init__()
        self.anki_generator = anki_generator
        self.front_tts_audio_generator = front_tts_audio_generator
        self.back_tts_audio_generator = back_tts_audio_generator
        self.image_creator = image_creator
        self.progress = progress

    # 使用 run 方法直接运行任务，而不是通过 moveToThread 和信号
    def run(self):
        if self.anki_generator is not None:
            self.anki_generator.generate(self.front_tts_audio_generator, self.back_tts_audio_generator, self.image_creator, self.progress)
            # run 方法结束时，QThread 的 finished 信号会自动发出