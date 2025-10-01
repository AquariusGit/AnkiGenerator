from PySide6.QtCore import QObject, Signal, Qt, Slot
from PySide6.QtWidgets import QProgressBar, QTextEdit
from PySide6.QtGui import QColor


from service.progress import Progress

class QtProgress(QObject, Progress):
    """
    一个用于Qt应用程序的Progress接口的具体实现。
    它使用信号和槽来安全地从任何线程更新QProgressBar和QTextEdit。
    """
    # 信号必须在类级别定义
    _progress_updated = Signal(int)
    _info_received = Signal(str)
    _warning_received = Signal(str)
    _error_received = Signal(str)
    _progress_reset = Signal()
    _progress_unknown = Signal()

    def __init__(self, progress_bar: QProgressBar, text_edit: QTextEdit):
        # 需要为两个父类都调用__init__
        QObject.__init__(self)
        Progress.__init__(self)

        self.progress_bar = progress_bar
        self.text_edit = text_edit

        # 连接信号到槽
        self._progress_updated.connect(self._set_progress)
        self._info_received.connect(self._append_info)
        self._warning_received.connect(self._append_warning)
        self._error_received.connect(self._append_error)
        self._progress_reset.connect(self._reset_progress_bar)
        self._progress_unknown.connect(self._set_progress_bar_unknown)

    # --- 槽 (在GUI线程中执行的私有方法) ---

    @Slot(int)
    def _set_progress(self, value: int):
        """设置进度条的值。"""
        if self.progress_bar.minimum() == 0 and self.progress_bar.maximum() == 0:
            # 如果进度条处于不确定模式，则重置其范围。
            self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(value)

    @Slot(str)
    def _append_info(self, text: str):
        """向文本编辑框追加一条信息性消息。"""
        self.text_edit.setTextColor(QColor("black"))
        self.text_edit.append(text)

    @Slot(str)
    def _append_warning(self, text: str):
        """向文本编辑框追加一条警告消息。"""
        self.text_edit.setTextColor(QColor("orange"))
        self.text_edit.append(f"警告: {text}")

    @Slot(str)
    def _append_error(self, text: str):
        """向文本编辑框追加一条错误消息。"""
        self.text_edit.setTextColor(QColor("red"))
        self.text_edit.append(f"错误: {text}")

    @Slot()
    def _reset_progress_bar(self):
        """将进度条重置为其初始状态。"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

    @Slot()
    def _set_progress_bar_unknown(self):
        """将进度条设置为不确定模式。"""
        self.progress_bar.setRange(0, 0)

    # --- 公共方法 (Progress接口的实现) ---
    # 这些方法是线程安全的，可以从任何线程调用。

    def update_progress(self, progress: int):
        self._progress_updated.emit(progress)

    def info(self, text: str):
        self._info_received.emit(text)        

    def warning(self, text: str):
        self._warning_received.emit(text)

    def error(self, text: str):
        self._error_received.emit(text)

    def update_info(self, progress: int, text: str):
        self.update_progress(progress)
        self.info(text)

    def update_error(self, progress: int, text: str):
        self.update_progress(progress)
        self.error(text)

    def update_warning(self, progress: int, text: str):
        self.update_progress(progress)
        self.warning(text)

    def reset_progress(self):
        self._progress_reset.emit()

    def set_progress_unknown(self):
        self._progress_unknown.emit()
