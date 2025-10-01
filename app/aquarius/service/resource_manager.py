import os
import json
import sys
from PySide6.QtCore import  QLocale


from entity.config_def import AppConfig

def is_not_blank(text: str) -> bool:
    return is_blank(text) is False

def is_blank(text: str) -> bool:
    if text is None or text.strip() == "":
        return True
    else:
        return False


class ResourceManager:

    
    """
    一个管理应用程序配置 (AppConfig) 的单例服务。
    这个类不应该在模块外部被直接实例化。
    """
    def __init__(self):
        # 使用默认配置进行初始化
        self._config: AppConfig = AppConfig()
        self.temp_files = []  # 实例属性初始化

        default_language = QLocale().name()
        self._config.language = default_language

        self._config.default_front_lang=default_language

        if default_language == "zh_CN":
            self._config.default_front_lang = "zh-hans"
            self._config.default_back_lang = "en"            
        else:
            self._config.default_front_lang = "en"
            self._config.default_back_lang = "zh-hans"
        

    def get_config(self) -> AppConfig:
        """返回单例的 AppConfig 实例。"""
        return self._config

# 模块首次导入时创建的单例实例。
_config_service = ResourceManager()

# 添加 tempfile 到列表
def add_temp_file( tempfile):
        _config_service.temp_files.append(tempfile)

def clear_temp_files():
    for tempfile in _config_service.temp_files:
        
        try:
            os.remove(tempfile)
        except Exception as e:
            print(e)
    
    _config_service.temp_files.clear()


def get_app_config() -> AppConfig:
    """
    提供对 AppConfig 单例实例的全局访问。
    """
    return _config_service.get_config()

def find_resource_in_installed_folder(filename: str) -> str:
    exe_path = os.path.abspath(sys.argv[0])
    exe_dir = os.path.dirname(exe_path)
    file_path = os.path.join(exe_dir, filename)
    return file_path

def find_resource_in_exec_folder(filename: str) -> str:

    if getattr(sys, 'frozen', False):

        base_dir = os.path.dirname(sys.executable)
        if getattr(sys, '_MEIPASS', None) is not None:
            internal_base_dir = os.path.join(base_dir, "_internal")
            if os.path.exists(internal_base_dir):
                base_dir = internal_base_dir

    else:
        # Running as script
        base_dir = os.path.dirname(sys.argv[0])

    return os.path.join(base_dir, filename)


def save_config(app_config: AppConfig, filename="config.json"):
    """
    将当前配置保存到指定的 JSON 文件中。
    """

    real_filename = find_resource_in_installed_folder(filename)    

    with open(real_filename, 'w', encoding='utf-8') as file:
        # json.dump(config_data, f, indent=4)
        jsonstr=json.dumps(app_config.__dict__, ensure_ascii=False,indent=4)
        file.write(jsonstr)

    print(f"配置已保存至 {real_filename}")

def save_last_media_folder(folder: str):
    app_config= _config_service.get_config()
    app_config.last_media_folder=folder

    save_config(app_config)

def save_download_folder(folder: str):
    app_config= _config_service.get_config()
    app_config.download_folder=folder

    save_config(app_config)

def load_config(app_config: AppConfig, filename="config.json"):

    """
    从指定的 JSON 文件中加载配置数据到 AppConfig 实例中。
    """
    try:
        real_filename = find_resource_in_installed_folder(filename)

        if not os.path.exists(real_filename):
            print(f"警告：文件 {real_filename} 未找到，使用默认配置。")
            return

        with open(real_filename, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        default_language = QLocale().name()

        app_config.__dict__.update(config_data)
        if is_blank(app_config.language):
            app_config.language = default_language
        
        

        print(f"配置已从 {real_filename} 加载成功。")
    except FileNotFoundError:
        print(f"警告：文件 {real_filename} 未找到，使用默认配置。")
    except json.JSONDecodeError:
        print(f"错误：{real_filename} 文件格式不正确，无法解析 JSON。")