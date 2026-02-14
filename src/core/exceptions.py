"""
自定义异常类 - 定义软件中的各种异常
支持错误码、用户友好消息和恢复建议
"""
from typing import Optional, Tuple


class ErrorCode:
    """错误码定义"""
    
    CONFIG_LOAD_FAILED = 'CONFIG_LOAD_FAILED'
    CONFIG_SAVE_FAILED = 'CONFIG_SAVE_FAILED'
    CONFIG_PARSE_ERROR = 'CONFIG_PARSE_ERROR'
    
    API_KEY_INVALID = 'API_KEY_INVALID'
    API_REQUEST_FAILED = 'API_REQUEST_FAILED'
    API_RATE_LIMIT = 'API_RATE_LIMIT'
    API_TIMEOUT = 'API_TIMEOUT'
    
    NETWORK_ERROR = 'NETWORK_ERROR'
    NETWORK_TIMEOUT = 'NETWORK_TIMEOUT'
    NETWORK_CONNECTION_FAILED = 'NETWORK_CONNECTION_FAILED'
    
    FILE_NOT_FOUND = 'FILE_NOT_FOUND'
    FILE_PERMISSION_DENIED = 'FILE_PERMISSION_DENIED'
    FILE_READ_ERROR = 'FILE_READ_ERROR'
    FILE_WRITE_ERROR = 'FILE_WRITE_ERROR'
    
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    INVALID_INPUT = 'INVALID_INPUT'
    
    GENERATION_FAILED = 'GENERATION_FAILED'
    EXPORT_FAILED = 'EXPORT_FAILED'


class MusicMakerException(Exception):
    """
    基础异常类
    
    支持错误码、用户友好消息和恢复建议，
    便于统一错误处理和用户提示。
    """
    
    ERROR_INFO: dict = {
        ErrorCode.CONFIG_LOAD_FAILED: ('配置加载失败', '请检查配置文件是否存在且格式正确'),
        ErrorCode.CONFIG_SAVE_FAILED: ('配置保存失败', '请检查是否有写入权限'),
        ErrorCode.CONFIG_PARSE_ERROR: ('配置解析错误', '请检查配置文件JSON格式是否正确'),
        
        ErrorCode.API_KEY_INVALID: ('API密钥无效', '请检查API密钥是否正确配置'),
        ErrorCode.API_REQUEST_FAILED: ('API请求失败', '请稍后重试或检查网络连接'),
        ErrorCode.API_RATE_LIMIT: ('API请求频率超限', '请稍后重试'),
        ErrorCode.API_TIMEOUT: ('API请求超时', '请检查网络连接或稍后重试'),
        
        ErrorCode.NETWORK_ERROR: ('网络错误', '请检查网络连接'),
        ErrorCode.NETWORK_TIMEOUT: ('网络连接超时', '请检查网络连接'),
        ErrorCode.NETWORK_CONNECTION_FAILED: ('无法连接到服务器', '请检查网络连接'),
        
        ErrorCode.FILE_NOT_FOUND: ('文件不存在', '请检查文件路径是否正确'),
        ErrorCode.FILE_PERMISSION_DENIED: ('文件权限不足', '请检查是否有访问权限'),
        ErrorCode.FILE_READ_ERROR: ('文件读取失败', '请检查文件是否存在且可读'),
        ErrorCode.FILE_WRITE_ERROR: ('文件写入失败', '请检查是否有写入权限'),
        
        ErrorCode.VALIDATION_ERROR: ('验证失败', '请检查输入是否正确'),
        ErrorCode.INVALID_INPUT: ('输入无效', '请检查输入内容'),
        
        ErrorCode.GENERATION_FAILED: ('生成失败', '请稍后重试'),
        ErrorCode.EXPORT_FAILED: ('导出失败', '请检查输出目录权限'),
    }
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: str = "",
        suggestion: Optional[str] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            code: 错误码
            details: 详细信息
            suggestion: 恢复建议
        """
        self.message = message
        self.code = code
        self.details = details
        self.suggestion = suggestion
        
        if code and code in self.ERROR_INFO:
            default_msg, default_suggestion = self.ERROR_INFO[code]
            if not suggestion:
                self.suggestion = default_suggestion
        
        super().__init__(self.message)
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.details:
            parts.append(f"详情: {self.details}")
        if self.suggestion:
            parts.append(f"建议: {self.suggestion}")
        return " | ".join(parts)
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            包含错误信息的字典
        """
        return {
            'message': self.message,
            'code': self.code,
            'details': self.details,
            'suggestion': self.suggestion
        }
    
    @classmethod
    def from_code(cls, code: str, details: str = "") -> 'MusicMakerException':
        """
        从错误码创建异常
        
        Args:
            code: 错误码
            details: 详细信息
        
        Returns:
            异常实例
        """
        if code in cls.ERROR_INFO:
            message, suggestion = cls.ERROR_INFO[code]
            return cls(message, code, details, suggestion)
        return cls(f"未知错误: {code}", code, details)


class ConfigException(MusicMakerException):
    """配置异常 - 配置文件加载或保存失败"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: str = "",
        suggestion: Optional[str] = None
    ):
        if not code:
            code = ErrorCode.CONFIG_LOAD_FAILED
        super().__init__(message, code, details, suggestion)


class APIException(MusicMakerException):
    """API调用异常 - AI模型API调用失败"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: str = "",
        suggestion: Optional[str] = None
    ):
        self.status_code = status_code
        if not code:
            code = ErrorCode.API_REQUEST_FAILED
        super().__init__(message, code, details, suggestion)


class PublishException(MusicMakerException):
    """发布异常 - 音乐平台发布失败"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: str = "",
        suggestion: Optional[str] = None
    ):
        super().__init__(message, code, details, suggestion)


class FileException(MusicMakerException):
    """文件异常 - 文件读写失败"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: str = "",
        suggestion: Optional[str] = None
    ):
        if not code:
            code = ErrorCode.FILE_READ_ERROR
        super().__init__(message, code, details, suggestion)


class NetworkException(MusicMakerException):
    """网络异常 - 网络连接或请求失败"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: str = "",
        suggestion: Optional[str] = None
    ):
        if not code:
            code = ErrorCode.NETWORK_ERROR
        super().__init__(message, code, details, suggestion)


class ValidationException(MusicMakerException):
    """验证异常 - 输入参数验证失败"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: str = "",
        suggestion: Optional[str] = None
    ):
        if not code:
            code = ErrorCode.VALIDATION_ERROR
        super().__init__(message, code, details, suggestion)
