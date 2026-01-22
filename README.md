# AI音乐创作桌面软件

基于Python+Flet开发的跨平台AI音乐创作桌面软件，支持调用AI模型生成歌词、旋律和编曲，并可一键发布到主流音乐平台。

## 功能特性

- 界面模块：现代化主界面、音频预览组件、状态提示栏、配置面板
- AI创作模块：支持OpenAI API，生成歌词、旋律（MIDI）、完整编曲
- 发布模块：封装网易云音乐、汽水音乐开放API，一键发布
- 辅助模块：本地文件保存、创作历史记录、异常处理

## 技术栈

- Python 3.10+
- Flet（GUI框架）
- requests（API调用）
- python-dotenv（密钥管理）
- librosa/midiutil（音乐处理）
- PyInstaller（打包）

## 项目结构

```
music-maker/
├── src/
│   ├── config/              # 配置管理模块
│   ├── core/                # 核心模块
│   ├── ai/                  # AI创作模块
│   ├── publish/             # 发布模块
│   └── ui/                  # 界面模块
├── main.py                  # 程序入口
├── requirements.txt         # 依赖列表
├── .env.example            # 配置模板
├── build.py                # 打包脚本
└── README.md               # 使用说明
```

## 安装步骤

### 1. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制配置模板并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写API密钥等信息：

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# 音乐平台配置
NETEASE_PHONE=your_phone_here
NETEASE_PASSWORD=your_password_here
QISHUI_ACCESS_TOKEN=your_access_token_here

# 应用配置
OUTPUT_DIR=./output
HISTORY_FILE=./history.json
```

## 运行方法

### 开发模式运行

```bash
python main.py
```

### 打包为可执行文件

```bash
python build.py
```

打包完成后，可执行文件位于 `dist/` 目录。

## 使用说明

### 创作功能

1. 在提示词输入框中输入创作需求
2. 选择风格、节拍、时长等参数
3. 点击"生成"按钮开始创作
4. 在预览区查看创作结果

### 发布功能

1. 切换到"发布"标签页
2. 选择要发布的音乐平台
3. 填写歌曲信息和上传音频文件
4. 点击"发布"按钮完成发布

### 配置管理

点击右上角设置按钮，可以配置：
- OpenAI API密钥
- 音乐平台账号
- 输出目录等

## 跨平台支持

本软件支持Windows、Mac、Linux三大平台，代码已做跨平台兼容处理。

## 注意事项

1. 首次运行需要配置API密钥
2. 确保网络连接正常
3. 生成的文件保存在output目录
4. 历史记录保存在history.json文件

## 许可证

MIT License
