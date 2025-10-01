import requests
import re
import subprocess
import json
from typing import List, Optional
from abc import ABC, abstractmethod
from PIL import Image
from io import BytesIO
import bs4
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import uuid
import time

from PySide6.QtCore import QCoreApplication

# 本地导入
from ui.qt_progress import Progress
from util.ruby import RubyAppenderFactory
from service.resource_manager import get_app_config


class BaseImageCreator(ABC):
    """
    图片创建器的抽象基类
    """

    def __init__(self):
        pass
    
    @abstractmethod
    def create_images(self, text:str, output_file:str, progress: Progress, timestamp: int = 0, quality=95) -> bool:
        """
        创建图片的抽象方法
        
        Args:
            text: 用于搜索图片的文本
            output_file: 输出文件路径
            progress: 进度对象
            timestamp: 时间戳（毫秒）
            quality: 图片质量
            
        Returns:
            bool: 创建成功返回True，否则返回False
        """
        pass


class BaseNetworkImageCreator(BaseImageCreator):
    """
    网络图片创建器的基类
    """

    def __init__(self):
        pass
    
    def create_images(self, text:str, output_file:str, progress: Progress, timestamp: int = 0, quality=95) -> bool:
        """
        从网络下载并创建图片
        
        Args:
            text: 用于搜索图片的文本
            output_file: 输出文件路径
            progress: 进程对象
            timestamp: 时间戳（毫秒）
            quality: 图片质量
            
        Returns:
            bool: 创建成功返回True，否则返回False
        """
        image_urls: List[str] = self.fetch_image_urls(text)

        if not image_urls: 
            return False
        
        # 尝试下载前五张图片
        for i, image_url in enumerate(image_urls[:5]):
            print(image_url)

            try:
                self.convert_image(image_url, output_file, quality)
                progress.info(QCoreApplication.translate("image_generator", "Successfully downloaded image for: {text}").format(text=text))
                return True
            except Exception as e:
                error_text = QCoreApplication.translate("image_generator", "Error while processing image for {text}: {error}").format(text=text, error=str(e))
                progress.error(error_text)

                # 如果是最后一张图片仍然失败，则返回False
                if i == 2 or i == len(image_urls[:3]) - 1:
                    break                
                
        return False

    @abstractmethod
    def fetch_image_urls(self, text:str) -> List[str]:
        """
        获取图片URL列表的抽象方法
        
        Args:
            text: 用于搜索图片的文本
            
        Returns:
            List[str]: 图片URL列表
        """
        pass

    def convert_image(self, image_url:str, output_file:str, quality=95):
        """
        转换并保存图片
        
        Args:
            image_url: 图片URL
            output_file: 输出文件路径
            quality: 图片质量
        """
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # 读取图片数据并转换为 PIL 对象
        img = Image.open(BytesIO(response.content))

        # 处理透明背景（如果是 PNG 等格式）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # 保存为 JPG
        img.save(output_file, 'JPEG', quality=quality)


class BaiduImageCreator(BaseNetworkImageCreator):
    """
    百度图片搜索创建器
    """
    
    def __init__(self):
        pass

    def fetch_image_urls(self, text: str) -> List[str]:
        url = f"https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={text}&ct=201326592&v=flip"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        return re.findall('"objURL":"(.*?)",', html, re.S)


class GoogleImageCreator(BaseNetworkImageCreator):
    """
    Google图片搜索创建器
    """
    
    def __init__(self):
        pass

    def fetch_image_urls(self, text: str) -> List[str]:
        search_url = f"https://www.google.com/search?q={text}&tbm=isch"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # 使用正则表达式提取图片URL
        return re.findall(r'https?://[^"\s]+?\.(?:jpg|jpeg|png|gif)', response.text)


class BingImageCreator(BaseNetworkImageCreator):
    """
    Bing图片搜索创建器
    """
    
    def __init__(self):
        pass

    def fetch_image_urls(self, text: str) -> List[str]:
        HEADERS = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
            )
        }

        """
        在 Bing 图片搜索中根据 query 提取第一张图片的原始 URL
        """
        search_url = f"https://www.bing.com/images/search?q={quote_plus(text)}&form=HDRSC2&first=1&tsc=ImageHoverTitle"
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # 新版 Bing 结果页中，图片真实 src 在 <a class="iusc"> 的 m 属性中（JSON 字符串）
        link_list = soup.find_all("a", class_="iusc")
        image_urls: List[str] = []

        for link in link_list:
            image_url = json.loads(link.get("m"))["murl"]  # type: ignore
            image_urls.append(image_url)

        return image_urls


class FfmpegImageCreator(BaseImageCreator):
    """
    使用FFmpeg从视频中截取图片的创建器
    """
    
    def __init__(self, video_file: str):
        self.video_file = video_file

    def create_images(self, text: str, output_file: str, progress: Progress, timestamp: int = 0, quality=1):
        """使用ffmpeg在指定时间戳截图"""
        try:
            # 将毫秒转换为 HH:MM:SS.mmm 格式
            timestamp_sec = timestamp / 1000
            # -y: 覆盖输出文件
            # -ss: 跳转到指定时间
            # -i: 输入文件
            # -vframes 1: 只截取一帧
            # -q:v: 设置图像质量 (1-31, 越低越好)
            command = [
                'ffmpeg',
                '-y',
                '-ss', str(timestamp_sec),
                '-i', self.video_file,
                '-vframes', '1',
                '-q:v', str(quality),
                output_file
            ]
            # 使用 subprocess.run 来更好地控制 ffmpeg 进程
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            info_text = QCoreApplication.translate("image_generator", "Take the {timestamp_sec} screenshot to {output_file}").format(timestamp_sec=timestamp_sec, output_file=output_file)
            progress.info(info_text)
            return True
        except FileNotFoundError as e:
            error_text = QCoreApplication.translate("image_generator", "Ffmpeg was not found,please check it.")
            progress.error(error_text)
            return False
        except subprocess.CalledProcessError as e:
            error_text = QCoreApplication.translate("image_generator", "Process error {error}.").format(error=str(e))
            progress.error(error_text)
            return False
        except Exception as e:
            error_text = QCoreApplication.translate("image_generator", "There was an error when taking the screenshot.")
            progress.error(error_text)    
            return False


class ImageCreatorFactory:
    """
    单例工厂类，用于根据配置获取适当的图片生成器实例
    """
    _instance = None
    _IMAGE_CREATOR_MAP = {
        "baidu": BaiduImageCreator(),
        "google": GoogleImageCreator(),
        "bing": BingImageCreator()
    }
    _default_image_creator = GoogleImageCreator()  # 默认使用Google获取图片

    
    def __new__(cls):
        """确保单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_default_image_creator(self) -> BaseImageCreator:
        """获取默认的图片生成器"""
        return self._default_image_creator
    
    def get_image_creator(self, image_creator_type: str) -> Optional[BaseImageCreator]:
        """获取指定的图片生成器"""
        return self._IMAGE_CREATOR_MAP.get(image_creator_type, None)