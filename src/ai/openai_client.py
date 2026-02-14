"""
OpenAI API客户端 - 封装OpenAI API调用
"""
import time
import json
import re
import requests
from typing import Dict, Any, Optional
from .base import BaseAIGenerator
from ..core.exceptions import APIException, NetworkException


class OpenAIClient(BaseAIGenerator):
    """OpenAI API客户端 - 封装OpenAI API调用"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化OpenAI客户端

        Args:
            config: 配置字典，包含api_key、api_base、model等
        """
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.api_base = config.get('api_base', 'https://api.openai.com/v1')
        self.model = config.get('model', 'gpt-4')
        self.timeout = 30
        self.max_retries = 3

    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送API请求

        Args:
            endpoint: API端点
            data: 请求数据

        Returns:
            响应数据

        Raises:
            APIException: API调用失败
            NetworkException: 网络错误
        """
        url = f"{self.api_base}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 401:
                    raise APIException("API密钥无效", status_code=401)

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                last_error = NetworkException("请求超时，请检查网络连接")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise last_error

            except requests.exceptions.RequestException as e:
                last_error = NetworkException(f"网络请求失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise last_error

        raise last_error or NetworkException("请求失败，未知错误")

    def generate_lyrics(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成歌词

        Args:
            prompt: 提示词
            **kwargs: 自定义参数（style, language等）

        Returns:
            生成结果字典
        """
        self._validate_prompt(prompt)

        style = kwargs.get('style', '流行')
        language = kwargs.get('language', '中文')

        system_prompt = f"""你是一位专业的歌词创作专家。请根据用户的需求创作歌词。
风格：{style}
语言：{language}

要求：
1. 歌词要有韵律感和节奏感
2. 内容要符合提示词的要求
3. 结构清晰，包含主歌、副歌等部分
4. 不要输出任何解释性文字，只输出歌词"""

        try:
            response = self._make_request('chat/completions', {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.8,
                'max_tokens': 2000
            })

            lyrics = response['choices'][0]['message']['content'].strip()

            metadata = {
                'model': self.model,
                'style': style,
                'language': language,
                'tokens_used': response.get('usage', {}).get('total_tokens', 0)
            }

            return self._format_result('lyrics', lyrics, metadata)

        except Exception as e:
            raise APIException("生成歌词失败", details=str(e))

    def generate_melody(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成旋律（MIDI格式）

        Args:
            prompt: 提示词
            **kwargs: 自定义参数（style, tempo, duration等）

        Returns:
            生成结果字典，包含MIDI音符数据
        """
        self._validate_prompt(prompt)

        style = kwargs.get('style', '流行')
        tempo = kwargs.get('tempo', 120)
        duration = kwargs.get('duration', 30)

        system_prompt = f"""你是一位专业的音乐作曲家。请根据用户的需求创作旋律。
风格：{style}
节拍：{tempo} BPM
时长：{duration}秒

要求：
1. 生成MIDI格式的音符数据
2. 每个音符包含：音高(pitch)、开始时间(start_time)、持续时间(duration)、力度(velocity)
3. 返回格式为JSON数组：[{{"pitch": 60, "start_time": 0, "duration": 0.5, "velocity": 80}}, ...]
4. 不要输出任何解释性文字，只输出JSON数组"""

        try:
            response = self._make_request('chat/completions', {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 1500
            })

            content = response['choices'][0]['message']['content'].strip()

            try:
                notes = json.loads(content)
            except json.JSONDecodeError:
                notes = self._parse_melody_from_text(content)

            metadata = {
                'model': self.model,
                'style': style,
                'tempo': tempo,
                'duration': duration,
                'notes_count': len(notes)
            }

            return self._format_result('melody', notes, metadata)

        except Exception as e:
            raise APIException("生成旋律失败", details=str(e))

    def generate_arrangement(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成完整编曲

        Args:
            prompt: 提示词
            **kwargs: 自定义参数（style, tempo, duration等）

        Returns:
            生成结果字典
        """
        self._validate_prompt(prompt)

        style = kwargs.get('style', '流行')
        tempo = kwargs.get('tempo', 120)
        duration = kwargs.get('duration', 60)

        system_prompt = f"""你是一位专业的音乐编曲家。请根据用户的需求创作完整编曲。
风格：{style}
节拍：{tempo} BPM
时长：{duration}秒

要求：
1. 生成多轨道的编曲数据
2. 包含主旋律、和声、贝斯、鼓等轨道
3. 每个音符包含：音高(pitch)、开始时间(start_time)、持续时间(duration)、力度(velocity)、轨道(track)
4. 返回格式为JSON：{{"tracks": [{{"name": "Melody", "notes": [...]}}, ...]}}
5. 不要输出任何解释性文字，只输出JSON"""

        try:
            response = self._make_request('chat/completions', {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 2000
            })

            content = response['choices'][0]['message']['content'].strip()

            try:
                arrangement = json.loads(content)
            except json.JSONDecodeError:
                arrangement = self._parse_arrangement_from_text(content)

            metadata = {
                'model': self.model,
                'style': style,
                'tempo': tempo,
                'duration': duration,
                'tracks_count': len(arrangement.get('tracks', []))
            }

            return self._format_result('arrangement', arrangement, metadata)

        except Exception as e:
            raise APIException("生成编曲失败", details=str(e))

    def _parse_melody_from_text(self, text: str) -> list:
        """
        从文本中解析旋律数据

        Args:
            text: 文本内容

        Returns:
            音符列表
        """
        notes = []
        pattern = r'pitch[:\s]+(\d+).*?start_time[:\s]+([\d.]+).*?duration[:\s]+([\d.]+).*?velocity[:\s]+(\d+)'

        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:
            notes.append({
                'pitch': int(match[0]),
                'start_time': float(match[1]),
                'duration': float(match[2]),
                'velocity': int(match[3])
            })

        return notes

    def _parse_arrangement_from_text(self, text: str) -> dict:
        """
        从文本中解析编曲数据

        Args:
            text: 文本内容

        Returns:
            编曲数据字典
        """
        tracks = []
        track_pattern = r'track[:\s]+(\w+).*?notes[:\s]+\[(.*?)\]'

        matches = re.findall(track_pattern, text, re.IGNORECASE | re.DOTALL)

        for match in matches:
            track_name = match[0]
            notes_text = match[1]

            notes = []
            note_pattern = r'\{.*?pitch[:\s]+(\d+).*?start_time[:\s]+([\d.]+).*?duration[:\s]+([\d.]+).*?velocity[:\s]+(\d+).*?\}'

            note_matches = re.findall(note_pattern, notes_text, re.IGNORECASE)

            for note_match in note_matches:
                notes.append({
                    'pitch': int(note_match[0]),
                    'start_time': float(note_match[1]),
                    'duration': float(note_match[2]),
                    'velocity': int(note_match[3])
                })

            tracks.append({
                'name': track_name,
                'notes': notes
            })

        return {'tracks': tracks}
