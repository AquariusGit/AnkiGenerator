from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QMainWindow, 
                              QMenuBar, QTabWidget, QMessageBox, QPushButton, 
                              QComboBox, QLineEdit, QFileDialog,QCheckBox)
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QObject, Signal, Slot, QThread
import yt_dlp

from typing import Any, Dict

import os
import re
import traceback
from typing import Optional, List, Dict
from ui.qt_progress import Progress,QtProgress
from entity.config_def import SubtitleConfig
from ui.helper import add_lang_to_combo_box,restore_lang_combobox,find_required_child
from ui.qt_progress import Progress,QtProgress
from service.resource_manager import find_resource_in_installed_folder,get_app_config,load_config,save_download_folder,save_last_media_folder,is_not_blank,is_blank
from util.localization import find_lang_by_display_name

from PySide6.QtCore import QCoreApplication
tr = QCoreApplication.translate  # 将 translate 重命名为 tr



class QueryVideoInfoThread(QThread):
    finished_signal = Signal(dict)  # 用于返回解析后的视频信息

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        
        ydl_opts: Dict[str, Any]  = {
            'quiet': True,
            'no_warnings': True,
            'listformats': True,
            'listsubtitles': True,
            'writesubtitles': True,
            'subtitlesformat': 'srt/vtt',
            'noplaylist': True,
            'skip_download': True,  # 仅查询信息，不下载
        }

        if get_app_config().support_auto_caption:
            ydl_opts['writeautomaticsub'] = True

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: # type: ignore
                info_dict = ydl.extract_info(self.url, download=False)
                self.finished_signal.emit(info_dict)
        except Exception as e:
            traceback.print_exc()
            self.finished_signal.emit({})

class DownloadThread(QThread):
    progress_signal = Signal(int)
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, url: str, output_dir: str, video_format: str,
             subtitle_config: SubtitleConfig,
             only_subtitles: bool = False, parent=None):
        super().__init__(parent)
        self.url = url
        self.output_dir = output_dir
        self.video_format = video_format
        self.front_lang =subtitle_config.front_lang
        self.back_lang = subtitle_config.back_lang
        self.only_subtitles = only_subtitles

        self._subtitle_config = subtitle_config

    def run(self):

        ydl_opts: Dict[str, Any]  = {
            'quiet': False,
            'no_warnings': False,
            'format': self.video_format + '+bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'writesubtitles': True,            
            'subtitlesformat': 'srt/vtt',
            'progress_hooks': [self._progress_hook],
            'noplaylist': True,
        }

        cookies_file_path = find_resource_in_installed_folder("cookies.txt")

        if os.path.exists(cookies_file_path):
            ydl_opts['cookiefile'] = cookies_file_path
            ydl_opts['writeautomaticsub'] = True


        # 如果仅下载字幕，跳过视频下载
        if self.only_subtitles:
            ydl_opts['skip_download'] = True

        # 跳过bilibili弹幕下载
        if "bilibili" in self.url:
            ydl_opts['ignore-danmaku'] = True            

        # 设置要下载的字幕语言
        subtitles = []
        if self.front_lang:
            subtitles.append(self.front_lang)
        if self.back_lang and self.back_lang != self.front_lang:
            subtitles.append(self.back_lang)

        if subtitles:
            ydl_opts['subtitleslangs'] = subtitles
        
        max_retries = 5  # 最大重试次数
        retry_count = 0

        base_delay = 5  # 基础延迟时间(秒)

        self.progress_signal.emit(10)

        while retry_count < max_retries:
            try:
                
                if retry_count == 0:
                    self.log_signal.emit(QCoreApplication.translate("download_form", "Starting download"))
                else:
                    self.log_signal.emit(QCoreApplication.translate("download_form", "Retrying download ({retry_count}/{max_retries})").format(retry_count=retry_count,max_retries=max_retries))
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: # type: ignore
                    info = ydl.extract_info(self.url, True)
                    
                    if self.only_subtitles:
                        self._subtitle_config.media_file = ""
                    else:
                        # 将下载得到的文件路径填充到 subtitle_config 中
                        self._subtitle_config.media_file = ydl.prepare_filename(info)
                    
                    # 通过 yt_dlp 返回的信息获取实际的字幕文件路径
                    requested_subtitles = info.get('requested_subtitles')
                    if isinstance(requested_subtitles, dict):
                        for lang, sub_info in requested_subtitles.items():
                            if 'filepath' in sub_info:
                                subtitle_file_path = sub_info['filepath']
                                if lang == self.front_lang:
                                    self._subtitle_config.front_subtitle_file = subtitle_file_path
                                elif lang == self.back_lang:
                                    self._subtitle_config.back_subtitle_file = subtitle_file_path
                    else:
                        # 如果无法从 info 中获取，使用原来的构造方式
                        if self.front_lang:
                            self._subtitle_config.front_subtitle_file = os.path.splitext(self._subtitle_config.media_file)[0] + f".{self.front_lang}.srt"
                            if not os.path.exists(self._subtitle_config.front_subtitle_file ):
                                self._subtitle_config.front_subtitle_file = os.path.splitext(self._subtitle_config.media_file)[0] + f".{self.front_lang}.vtt"
                    
                        if self.back_lang and self.back_lang != self.front_lang:                
                            self._subtitle_config.back_subtitle_file = os.path.splitext(self._subtitle_config.media_file)[0] + f".{self.back_lang}.srt"
                            if not os.path.exists(self._subtitle_config.back_subtitle_file ):
                                self._subtitle_config.back_subtitle_file = os.path.splitext(self._subtitle_config.media_file)[0] + f".{self.back_lang}.vtt"

                self.progress_signal.emit(100)
                self.log_signal.emit(QCoreApplication.translate("download_form", "Download completed."))
                self.finished_signal.emit(True, QCoreApplication.translate("download_form", "Download succeeded."))
                return  # 成功下载后直接返回
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    # 达到最大重试次数，发送失败信号
                    traceback.print_exc()
                    error_msg = str(e)
                    if retry_count > 1:
                        error_msg = QCoreApplication.translate("download_form", "After {retry_count} retries, still failed: {error_msg}").format(retry_count=retry_count, error_msg=error_msg)
                    self.finished_signal.emit(False, error_msg)
                else:

                    delay = base_delay * (2 ** (retry_count - 1))  # 每次重试加倍延迟
                
                    # 等待一段时间再重试
                    self.log_signal.emit(QCoreApplication.translate("download_form", "Download failed, retrying in 5 seconds..."))
                    # 简单的等待实现（可以按需替换为更精确的定时器）
                    import time
                    time.sleep(delay)

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip('%')
            try:
                self.progress_signal.emit(int(float(percent)))
            except:
                pass

            download_info=QCoreApplication.translate("download_form", "Downloading: {file} - {percent}%").format(file=d.get('filename', ''), percent=percent)            
            self.log_signal.emit(download_info)

class DownloadFormController(QObject):
    # 定义 signal，在下载完成后发射
    request_generate_from_subtitle = Signal(object)  # 参数为 SyncSubtitleConfig 或 SubtitleConfig 对象


    def __init__(self, download_form: QWidget,   progress: QtProgress):
        super().__init__()
        self.download_form = download_form
        self.progress = progress

        # 修改后：
        self.query_thread: Optional[QueryVideoInfoThread] = None
        self.download_thread: Optional[DownloadThread] = None

        self.subtitle_config :SubtitleConfig=SubtitleConfig()

        self._fetch_children()
        self.reset_ui_state()
        self._connect_signals()

    def _fetch_children(self):
        """
        Fetches and assigns all the required child widgets from the download_form.
        """
        
    
        self.url_edit  = find_required_child(self.download_form, QLineEdit, "url_edit")
        self.url_check_checkbox = find_required_child(self.download_form, QCheckBox, "url_check_checkbox")
        self.query_url_button = find_required_child(self.download_form, QPushButton, "query_url_button")
    
        self.download_directory_edit = find_required_child(self.download_form, QLineEdit, "download_directory_edit")
        self.download_directory_browse_button = find_required_child(self.download_form, QPushButton, "download_directory_browse_button")
    
        self.audio_video_format_combobox = find_required_child(self.download_form, QComboBox, "audio_video_format_combobox")
        self.front_lang_combobox = find_required_child(self.download_form, QComboBox, "front_lang_combobox")
        self.back_lang_combobox = find_required_child(self.download_form, QComboBox, "back_lang_combobox")
    
        self.only_download_subtitle_checkbox = find_required_child(self.download_form, QCheckBox, "only_download_subtitle_checkbox")
        self.download_button = find_required_child(self.download_form, QPushButton, "download_button")

    def reset_ui_state(self):
        self.audio_video_format_combobox.clear()
        self.front_lang_combobox.clear()
        self.back_lang_combobox.clear()

        self.progress.reset_progress()

    def _connect_signals(self):
        """Connects widget signals to controller slots."""
        self.query_url_button.clicked.connect(self._on_query_url_clicked)
        self.download_directory_browse_button.clicked.connect(self._on_download_directory_browse_clicked)
        self.download_button.clicked.connect(self._on_download_button_clicked)  # 新增

        # url_edit控件输入Enter键时，触发查询按钮点击事件
        self.url_edit.returnPressed.connect(self._on_query_url_clicked)

    def _on_query_url_clicked(self):

        if (self.query_thread is not None and self.query_thread.isRunning() ) and (self.download_thread is not None and self.download_thread.isRunning() ):
            QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","wait"), QCoreApplication.translate("download_form","Please wait for the current task to finish."))
            return

        self.reset_ui_state()

        """
        Validates the URL from the url_edit field when the query button is clicked.
        If url_check_checkbox is checked, it validates for a YouTube URL.
        Otherwise, it performs a basic HTTP/HTTPS check.
        """
        url = self.url_edit.text().strip()
        if is_blank(url):
            QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","warning"), QCoreApplication.translate("download_form","Please use the right video url."))
            
            return

        is_valid = False
        if self.url_check_checkbox.isChecked():
            # Standard YouTube video URL regex
            youtube_regex = re.compile(r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/).+')
            if youtube_regex.match(url):
                is_valid = True
        else:
            if url.startswith("http://") or url.startswith("https://"):
                is_valid = True

        if not is_valid:
            QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","warning"), QCoreApplication.translate("download_form","Please use the right video url."))            
            return

        self.progress._set_progress(20)
        progress_info=QCoreApplication.translate("download_form","Start querying video {url} info...")
        progress_info=progress_info.format(url=url)
        
        self.progress.info(progress_info)

        # 启动后台线程进行查询
        self.query_thread = QueryVideoInfoThread(url)
        self.query_thread.finished_signal.connect(self._on_query_finished)
        self.query_thread.start()
        
    

    def _on_download_directory_browse_clicked(self):
        """Handle browse button click to select download directory."""
        selected_dir = QFileDialog.getExistingDirectory(self.download_form, QCoreApplication.translate("download_form", "Select download directory"),dir=get_app_config().download_folder)
        if selected_dir:
            self.download_directory_edit.setText(selected_dir)
            save_download_folder(selected_dir)

    def _on_download_button_clicked(self):

        if (self.query_thread is not None and self.query_thread.isRunning() ) and (self.download_thread is not None and self.download_thread.isRunning() ):
            QMessageBox.warning(self.download_form, "Wait", "Please wait for the current task to finish.")
            return
    
        url = self.url_edit.text()
        if is_blank(url):
            QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","warning"), QCoreApplication.translate("download_form","Please use the right video url."))            
            return

        output_dir = self.download_directory_edit.text().strip()
        if is_blank(url) or not os.path.isdir(output_dir):
            QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","warning"), QCoreApplication.translate("download_form","Please select a valid download directory."))            
            return

        video_format = self.audio_video_format_combobox.currentData().strip()
        if is_blank(video_format):
            QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","warning"), QCoreApplication.translate("download_form","Please select a video format."))            
            return

        # 获取原始语言代码（通过 itemData）
        front_lang = self.front_lang_combobox.currentData()
        back_lang = self.back_lang_combobox.currentData()

        if is_not_blank(front_lang) or is_not_blank(back_lang):
            if front_lang == back_lang:
                QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","warning"), QCoreApplication.translate("download_form","Please select different subtitle languages."))            
                return

        # 新增：判断是否只下载字幕
        only_subtitles = self.only_download_subtitle_checkbox.isChecked()

        if only_subtitles:
            if is_blank(front_lang) or is_blank(back_lang):
                QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","warning"), QCoreApplication.translate("download_form","Please select front and back subtitle languages."))            
                return

        self.subtitle_config.front_lang=front_lang
        self.subtitle_config.back_lang=back_lang

        # 启动下载线程
        self.download_thread = DownloadThread(url, output_dir, video_format, self.subtitle_config,only_subtitles)
        self.download_thread.progress_signal.connect(self.progress._set_progress)
        self.download_thread.log_signal.connect(self.progress.info)
        self.download_thread.finished_signal.connect(self._on_download_finished)
        
        self.download_thread.start()

    def _on_query_finished(self, info_dict: dict):

        supported_formats = {'webm', 'mp4', 'mp3', 'm4a'}

        # 提取可用的格式并构建更友好的显示文本
        formats = info_dict.get('formats', [])
        for f in formats:
            if 'format_id' not in f:
                continue

            ext = f.get('ext')
            if ext not in supported_formats:
                continue  # 跳过不支持的格式

            format_id = f['format_id']
            resolution = f"{f.get('width', '?')}x{f.get('height', '?')}" if 'height' in f else 'Audio'
            filesize = f.get('filesize_approx', f.get('filesize', None))
            filesize_str = f"~{round(filesize / (1024 * 1024))}MB" if filesize else ""

            display_text = f"{format_id} - {resolution} ({ext.upper()}, {filesize_str})".replace(" (~", " (~").replace(", )", ")")

            self.audio_video_format_combobox.addItem(display_text, format_id)
		
        # 在 _on_query_finished 方法中改进字幕处理逻辑
        subtitles = info_dict.get('subtitles', {})
        automatic_captions = info_dict.get('automatic_captions', {})

        # 合并手动和自动字幕
        all_subtitles = {}
        
        if get_app_config().support_auto_caption:
            all_subtitles.update(automatic_captions)
        
        all_subtitles.update(subtitles)

        # 然后处理 all_subtitles 而不是单独处理 subtitles 和 automatic_captions

        srt_langs = [
            lang for lang, sub_info in all_subtitles.items()
            if any(item.get('ext') in ['srt', 'vtt'] for item in sub_info)
        ]

        for lang in srt_langs:
            # display_name = find_lang_by_display_name(lang)
            # self.front_lang_combobox.addItem(display_name, lang)
            # self.back_lang_combobox.addItem(display_name, lang)

            self.front_lang_combobox.addItem(lang, lang)
            self.back_lang_combobox.addItem(lang, lang)

        app_config = get_app_config()
        restore_lang_combobox(app_config.default_front_lang,self.front_lang_combobox)
        restore_lang_combobox(app_config.default_back_lang,self.back_lang_combobox)

        self.progress._set_progress(0)
        self.progress.info(QCoreApplication.translate("download_form", "Querying video information completed"))

        if self.query_thread is not None:
            self.query_thread.wait()
            self.query_thread.quit()
            self.query_thread.deleteLater()
            self.query_thread=None
        

    def _on_download_finished(self, success: bool, message: str):

        if success:
            # Ask the user if they want to proceed to the next page
            reply = QMessageBox.question(
                self.download_form,
                QCoreApplication.translate("download_form", "Downloading was completed"),  # Title: Download Complete
                 QCoreApplication.translate("download_form", "Download successful! Go to the subtitle processing page now"),  # Message: Download successful! Go to the subtitle processing page now?
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes  # Default button
            )

            if reply == QMessageBox.StandardButton.Yes:
                # NOTE: This assumes `SyncSubtitleConfig` has a method to update its state
                # from the `SubtitleConfig` object populated by the download thread.
                # fixme
                self.request_generate_from_subtitle.emit(self.subtitle_config)

        else:
            if not message:
                message=""                
            
            message_text=QCoreApplication.translate("download_form","Download failed: {message}").format(message)
            QMessageBox.warning(self.download_form, QCoreApplication.translate("download_form","error"), message_text)

        if self.download_thread is not None:
            self.download_thread.wait()
            self.download_thread.quit()
            self.download_thread.deleteLater()
            self.download_thread=None