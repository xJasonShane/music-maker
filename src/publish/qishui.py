"""
汽水音乐发布器 - 封装汽水音乐API
"""
import requests
from typing import Dict, Any
from .base import BasePublisher
from ..core.exceptions import PublishException, NetworkException


class QishuiPublisher(BasePublisher):
    """汽水音乐发布器 - 封装汽水音乐API"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化汽水音乐发布器

        Args:
            config: 配置字典，包含access_token等
        """
        super().__init__(config)
        self.access_token = config.get('access_token', '')
        self.base_url = 'https://open-api.qishui.com'
        self._session = None

    def authenticate(self) -> bool:
        """
        认证

        Returns:
            是否认证成功
        """
        if not self.access_token:
            raise PublishException("访问令牌未配置")

        try:
            self._session = requests.Session()

            response = self._session.get(
                f'{self.base_url}/v1/user/info',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'User-Agent': 'Mozilla/5.0'
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
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
                f'{self.base_url}/v1/music/upload',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'User-Agent': 'Mozilla/5.0'
                },
                data={
                    'title': title,
                    'lyrics': lyrics
                },
                files={'audio': audio_data}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    music_id = data.get('data', {}).get('music_id')

                    return {
                        'success': True,
                        'platform': 'qishui',
                        'music_id': music_id,
                        'title': title,
                        'url': f'https://qishui.com/music/{music_id}'
                    }
                else:
                    raise PublishException(f"上传失败: {data.get('message', '未知错误')}")
            else:
                raise NetworkException(f"网络请求失败: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise NetworkException(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise PublishException(f"发布失败: {str(e)}")
