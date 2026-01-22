# AI音乐创作桌面软件

基于 Python + Flet 开发的跨平台 AI 音乐创作桌面软件，支持调用 AI 模型生成歌词、旋律和编曲，并可一键发布到主流音乐平台。

## 快速开始

### 最快上手方式

```bash
# 1. 克隆项目
git clone <repository-url>
cd music-maker

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写必要的 API 密钥

# 4. 运行程序
python main.py
```

> **提示**：首次运行前请确保已配置 OpenAI API 密钥

## 系统要求

- **操作系统**：Windows 10+ / macOS 10.14+ / Linux (Ubuntu 18.04+)
- **Python 版本**：3.10 或更高
- **内存**：建议 4GB 以上
- **网络**：需要稳定的互联网连接（调用 AI API）

## 功能特性

### 核心功能

- **AI 创作引擎**
  - 智能歌词生成：支持多种风格、主题和情感
  - 旋律创作：自动生成 MIDI 格式的旋律
  - 完整编曲：生成包含多轨道的完整音乐作品

- **可视化界面**
  - 现代化主界面设计，操作直观
  - 实时音频预览组件
  - 状态提示栏，实时反馈创作进度
  - 配置面板，灵活管理各项参数

- **一键发布**
  - 集成网易云音乐开放 API
  - 集成汽水音乐开放 API
  - 支持批量发布到多个平台

- **创作管理**
  - 本地文件自动保存
  - 创作历史记录追踪
  - 完善的异常处理机制

### 使用场景

- 音乐爱好者快速创作灵感
- 内容创作者生成背景音乐
- 独立音乐人辅助创作
- 音乐教育演示工具

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 核心开发语言 |
| Flet | 最新版 | 跨平台 GUI 框架 |
| requests | - | HTTP 请求处理 |
| python-dotenv | - | 环境变量管理 |
| librosa | - | 音频处理与分析 |
| midiutil | - | MIDI 文件生成 |
| PyInstaller | - | 可执行文件打包 |

**技术选型理由：**
- **Flet**：基于 Flutter，提供原生性能和现代化 UI，支持三大平台
- **librosa**：Python 音频处理领域的标准库，功能强大
- **PyInstaller**：成熟的打包工具，兼容性好

## 项目结构

```
music-maker/
├── src/
│   ├── config/              # 配置管理模块
│   │   ├── __init__.py
│   │   └── settings.py      # 配置加载与验证
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   └── exceptions.py    # 自定义异常类
│   ├── ai/                  # AI 创作模块
│   │   ├── __init__.py
│   │   ├── lyrics.py        # 歌词生成
│   │   ├── melody.py        # 旋律生成
│   │   └── arrangement.py   # 编曲生成
│   ├── publish/             # 发布模块
│   │   ├── __init__.py
│   │   ├── netease.py       # 网易云音乐接口
│   │   └── qishui.py        # 汽水音乐接口
│   └── ui/                  # 界面模块
│       ├── __init__.py
│       ├── main_window.py   # 主窗口
│       ├── preview.py       # 音频预览组件
│       └── settings.py      # 设置面板
├── main.py                  # 程序入口
├── requirements.txt         # 依赖列表
├── .env.example            # 配置模板
├── .env                    # 环境变量（需自行创建）
├── build.py                # 打包脚本
├── output/                 # 输出目录（自动创建）
├── history.json            # 历史记录（自动生成）
└── README.md               # 使用说明
```

## 详细安装步骤

### 1. 创建虚拟环境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

如果安装速度慢，可使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置环境变量

复制配置模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下信息：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# 音乐平台配置（可选）
NETEASE_PHONE=your_phone_here
NETEASE_PASSWORD=your_password_here
QISHUI_ACCESS_TOKEN=your_access_token_here

# 应用配置
OUTPUT_DIR=./output
HISTORY_FILE=./history.json
```

> **安全提示**：不要将 `.env` 文件提交到版本控制系统

## 使用指南

### 创作流程

1. **启动程序**
   ```bash
   python main.py
   ```

2. **输入创作需求**
   - 在提示词输入框中描述你的创作想法
   - 例如："一首关于夏天的轻快流行歌曲"

3. **配置参数**
   - 选择音乐风格（流行、摇滚、电子、古典等）
   - 设置节拍（BPM）
   - 设定时长（秒）

4. **生成音乐**
   - 点击"生成"按钮
   - 等待 AI 完成创作
   - 在预览区查看结果

5. **保存作品**
   - 满意后点击"保存"
   - 文件将保存到 `output/` 目录

### 发布流程

1. **切换到发布标签页**

2. **选择平台**
   - 网易云音乐
   - 汽水音乐

3. **填写信息**
   - 歌曲名称
   - 歌手信息
   - 封面图片（可选）
   - 歌词（可选）

4. **上传音频**
   - 选择本地音频文件
   - 支持格式：MP3, WAV, FLAC

5. **发布**
   - 点击"发布"按钮
   - 等待上传完成

### 配置管理

点击右上角设置按钮，可以配置：
- OpenAI API 密钥和模型
- 音乐平台账号信息
- 输出目录路径
- 默认创作参数

## 打包发布

### 打包为可执行文件

```bash
python build.py
```

打包完成后，可执行文件位于 `dist/` 目录：
- Windows: `dist/music-maker.exe`
- macOS: `dist/music-maker.app`
- Linux: `dist/music-maker`

### 分发说明

打包后的可执行文件可以直接分发，用户无需安装 Python 环境。

## 常见问题（FAQ）

### Q1: 提示"API 密钥无效"怎么办？

**A:** 请检查：
1. `.env` 文件中的 `OPENAI_API_KEY` 是否正确
2. API 密钥是否已激活且有余额
3. 网络连接是否正常

### Q2: 生成的音乐质量不理想？

**A:** 可以尝试：
1. 调整提示词，更详细地描述需求
2. 尝试不同的 AI 模型（如 gpt-4-turbo）
3. 多次生成，选择最佳版本

### Q3: 发布失败怎么办？

**A:** 常见原因：
1. 平台账号未登录或已过期
2. 音频文件格式不支持
3. 网络连接问题
4. 平台 API 限制

### Q4: 可以离线使用吗？

**A:** 不可以。本软件需要调用在线 AI API，必须保持网络连接。

### Q5: 支持哪些音频格式？

**A:** 
- 输入：MP3, WAV, FLAC, OGG
- 输出：MIDI（旋律）、WAV（完整编曲）

### Q6: 如何卸载？

**A:** 
- 开发模式：直接删除项目目录
- 打包版本：删除可执行文件和 `output/`、`history.json` 文件

## 开发说明

### 添加新的 AI 模型

1. 在 `src/ai/` 目录下创建新的模块
2. 实现统一的接口规范
3. 在配置文件中注册新模型

### 添加新的发布平台

1. 在 `src/publish/` 目录下创建新的模块
2. 实现平台的 API 接口
3. 在 UI 中添加对应的发布选项

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
git clone <repository-url>
cd music-maker
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

## 许可证

GPL-V3 License - 详见 [LICENSE](LICENSE) 文件

---

**享受音乐创作的乐趣！** 🎵
