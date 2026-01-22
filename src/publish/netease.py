"""
网易云音乐发布器 - 封装网易云音乐API
"""
import hashlib
import requests
from typing import Dict, Any
from .base import BasePublisher
from ..core.exceptions import PublishException, NetworkException


class NeteasePublisher(BasePublisher):
    """网易云音乐发布器 - 封装网易云音乐API"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化网易云音乐发布器

        Args:
            config: 配置字典，包含phone、password等
        """
        super().__init__(config)
        self.phone = config.get('phone', '')
        self.password = config.get('password', '')
        self.base_url = 'https://music.163.com'
        self._session = None

    def authenticate(self) -> bool:
        """
        认证

        Returns:
            是否认证成功
        """
        if not self.phone or not self.password:
            raise PublishException("手机号或密码未配置")

        try:
            self._session = requests.Session()

            encrypted_password = self._encrypt_password(self.password)

            response = self._session.post(
                f'{self.base_url}/weapi/login/cellphone',
                json={
                    'phone': self.phone,
                    'password': encrypted_password,
                    'rememberLogin': True
                },
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    self._authenticated = True
                    return True
                else:
                    raise PublishException(f"认证失败: {data.get('message', '未知错误')}")
            else:
                raise NetworkException(f"网络请求失败: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise NetworkException(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise PublishException(f"认证失败: {str(e)}")

    def publish(self, title: str, audio_file: str, **kwargs) -> Dict[str, Any]:
        """
        发布音乐

        Args:
            title: 歌曲标题
            audio_file: 音频文件路径
            **kwargs: 其他参数（lyrics, cover等）

        Returns:
            发布结果字典
        """
        self._validate_audio_file(audio_file)

        if not self.is_authenticated():
            if not self.authenticate():
                raise PublishException("认证失败，无法发布")

        lyrics = kwargs.get('lyrics', '')
        cover = kwargs.get('cover', '')

        try:
            with open(audio_file, 'rb') as f:
                audio_data = f.read()

            response = self._session.post(
                f'{self.base_url}/weapi/cloud/detect',
                data={'songId': 0},
                files={'songFile': audio_data},
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    song_id = data.get('result', {}).get('songId')

                    return {
                        'success': True,
                        'platform': 'netease',
                        'song_id': song_id,
                        'title': title,
                        'url': f'https://music.163.com/#/song?id={song_id}'
                    }
                else:
                    raise PublishException(f"上传失败: {data.get('message', '未知错误')}")
            else:
                raise NetworkException(f"网络请求失败: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise NetworkException(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise PublishException(f"发布失败: {str(e)}")

    def _encrypt_password(self, password: str) -> str:
        """
        加密密码（网易云音乐使用MD5加密）

        Args:
            password: 原始密码

        Returns:
            加密后的密码
        """
        return hashlib.md5(password.encode()).hexdigest()
