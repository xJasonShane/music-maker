"""
自定义异常类 - 定义软件中的各种异常
"""


class MusicMakerException(Exception):
    """基础异常类"""

    def __init__(self, message: str, details: str = ""):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ConfigException(MusicMakerException):
    """配置异常 - 配置文件加载或保存失败"""

    pass


class APIException(MusicMakerException):
    """API调用异常 - AI模型API调用失败"""

    def __init__(self, message: str, status_code: int = None, details: str = ""):
        self.status_code = status_code
        super().__init__(message, details)


class PublishException(MusicMakerException):
    """发布异常 - 音乐平台发布失败"""

    pass


class FileException(MusicMakerException):
    """文件异常 - 文件读写失败"""

    pass


class NetworkException(MusicMakerException):
    """网络异常 - 网络连接或请求失败"""

    pass


class ValidationException(MusicMakerException):
    """验证异常 - 输入参数验证失败"""

    pass
