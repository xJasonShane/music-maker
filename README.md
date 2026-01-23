# 音悦 - AI音乐创作桌面软件

基于 Python + Flet 开发的跨平台 AI 音乐创作桌面软件，支持调用多种 AI 模型生成歌词、旋律和编曲。

## 快速开始

### 最快上手方式

```bash
# 1. 克隆项目
git clone <repository-url>
cd music-maker

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python main.py
```

> **提示**：首次运行后，在软件设置中配置 AI 模型 API 密钥

## 系统要求

- **操作系统**：Windows 10+ / macOS 10.14+ / Linux (Ubuntu 18.04+)
- **Python 版本**：3.10 或更高
- **内存**：建议 4GB 以上
- **网络**：需要稳定的互联网连接（调用 AI API）

## 功能特性

### 核心功能

- **多模型 AI 创作引擎**
  - 支持 OpenAI、Claude、通义千问、文心一言等多种 AI 模型
  - 智能歌词生成：支持多种风格、主题和情感
  - 旋律创作：自动生成 MIDI 格式的旋律
  - 完整编曲：生成包含多轨道的完整音乐作品

- **可视化界面**
  - 现代化主界面设计，操作直观
  - 实时音频预览组件
  - 状态提示栏，实时反馈创作进度
  - 配置面板，灵活管理各项参数

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
│   │   └── config_manager.py # 配置加载与验证（支持多模型）
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   ├── exceptions.py    # 自定义异常类
│   │   ├── file_manager.py  # 文件管理
│   │   └── history_manager.py # 历史记录管理
│   ├── ai/                  # AI 创作模块
│   │   ├── __init__.py
│   │   ├── base.py          # 基础接口
│   │   ├── generator.py     # 音乐生成器（支持多模型切换）
│   │   └── openai_client.py # OpenAI 客户端
│   └── ui/                  # 界面模块
│       ├── __init__.py
│       ├── main_window.py   # 主窗口（含模型选择）
│       ├── audio_player.py  # 音频播放器
│       └── config_panel.py  # 配置面板（支持多模型配置）
├── main.py                  # 程序入口
├── requirements.txt         # 依赖列表
├── .env.example            # 配置模板
├── config.json             # 运行时配置（自动生成）
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

### 3. 配置环境变量（可选）

复制配置模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置应用参数：

```env
# 应用配置
OUTPUT_DIR=./output
HISTORY_FILE=./history.json
```

> **注意**：API 密钥现在直接在软件中配置，无需在 `.env` 文件中设置

## 详细使用指南

### 首次启动配置

1. **启动程序**

   ```bash
   python main.py
   ```

2. **打开设置面板**
   - 点击右上角的设置图标（齿轮按钮）

3. **配置 AI 模型**
   - 在设置面板中可以看到多个模型配置卡片：
     - **OpenAI**：支持 GPT-4、GPT-3.5 等模型
     - **Claude**：Anthropic 的 Claude 系列
     - **通义千问**：阿里云的大语言模型
     - **文心一言**：百度的文心系列

4. **填写模型信息**
   - 勾选"启用"开关来激活模型
   - 填写 API 密钥
   - 设置 API 地址（通常有默认值）
   - 指定模型名称（如 gpt-4、claude-3-opus 等）

5. **选择默认模型**
   - 点击模型卡片右侧的勾选按钮选择当前使用的模型
   - 当前选中的模型会有蓝色边框高亮显示

6. **保存配置**
   - 点击"保存配置"按钮
   - 配置会自动保存到 `config.json` 文件
   - 无需重启程序，配置立即生效

### 创作流程

1. **选择 AI 模型**
   - 在创作区的"AI 模型"下拉框中选择要使用的模型
   - 只有已启用且配置了 API 密钥的模型才会显示

2. **输入创作需求**
   - 在提示词输入框中描述你的创作想法
   - 例如："一首关于夏天的轻快流行歌曲"
   - 可以详细描述风格、情感、主题等

3. **配置参数**
   - **音乐风格**：流行、摇滚、古典、电子、民谣、爵士
   - **节拍（BPM）**：60、90、120、140、180
   - **时长（秒）**：30、60、90、120

4. **生成音乐**
   - 点击"生成"按钮
   - 等待 AI 完成创作
   - 状态栏会显示"正在生成..."
   - 生成完成后会在预览区显示结果

5. **预览和保存**
   - 在预览区查看生成的歌词或旋律
   - 使用音频播放器预览（如果支持）
   - 满意后可以保存到本地

### 配置管理

#### 模型配置

点击右上角设置按钮，可以配置：

1. **启用/禁用模型**
   - 通过开关控制哪些模型可用
   - 禁用的模型不会出现在主界面的选择列表中

2. **API 密钥管理**
   - 每个模型独立配置 API 密钥
   - 密钥以密码形式显示，可点击眼睛图标查看

3. **API 地址设置**
   - 可以自定义 API 端点
   - 支持代理或自建服务

4. **模型名称**
   - 指定具体使用的模型版本
   - 如：gpt-4、gpt-3.5-turbo、claude-3-opus 等

#### 应用配置

- **输出目录**：设置生成文件的保存路径
- **历史记录文件**：设置创作历史的存储位置

### 模型切换

在创作过程中，可以随时切换 AI 模型：

1. 在创作区的"AI 模型"下拉框中选择其他模型
2. 状态栏会显示"已切换到 XXX 模型"
3. 重新点击"生成"即可使用新模型

### 历史记录

- 每次创作都会自动保存到历史记录
- 历史记录包含：提示词、模型、参数、结果
- 通过导航栏的"历史"标签查看所有历史记录
- 点击任意历史记录可查看详细信息（包含提示词和创作结果）
- 支持刷新历史记录列表
- 支持返回历史记录列表

## 支持的 AI 模型

### OpenAI

- **模型**：GPT-4、GPT-3.5 Turbo
- **API 地址**：<https://api.openai.com/v1>
- **特点**：功能强大，支持复杂任务

### Claude (Anthropic)

- **模型**：Claude 3 Opus、Sonnet、Haiku
- **API 地址**：<https://api.anthropic.com/v1>
- **特点**：上下文理解能力强

### 通义千问 (阿里云)

- **模型**：Qwen-Max、Qwen-Plus、Qwen-Turbo
- **API 地址**：<https://dashscope.aliyuncs.com/compatible-mode/v1>
- **特点**：中文优化，性价比高

### 文心一言 (百度)

- **模型**：ERNIE-Bot 4、ERNIE-Bot 3.5
- **API 地址**：<https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop>
- **特点**：中文理解深入

## 打包发布

### 打包为可执行文件

```bash
python build.py
```

打包完成后，可执行文件位于 `dist/` 目录：
- Windows: `dist/音悦.exe`
- macOS: `dist/音悦.app`
- Linux: `dist/音悦`

### 分发说明

打包后的可执行文件可以直接分发，用户无需安装 Python 环境。

## 常见问题（FAQ）

### Q1: 首次启动需要配置什么？

**A:** 首次启动需要：

1. 点击右上角设置按钮
2. 在设置面板中启用至少一个 AI 模型
3. 填写该模型的 API 密钥
4. 点击保存配置

### Q2: 如何获取 API 密钥？

**A:** 各模型的 API 密钥获取方式：

- **OpenAI**：访问 <https://platform.openai.com/api-keys>
- **Claude**：访问 <https://console.anthropic.com/>
- **通义千问**：访问 <https://dashscope.console.aliyun.com/>
- **文心一言**：访问 <https://cloud.baidu.com/product/wenxinworkshop>

### Q3: 提示"API 密钥无效"怎么办？

**A:** 请检查：

1. 设置面板中的 API 密钥是否正确
2. API 密钥是否已激活且有余额
3. 网络连接是否正常
4. API 地址是否正确

### Q4: 生成的音乐质量不理想？

**A:** 可以尝试：

1. 调整提示词，更详细地描述需求
2. 尝试不同的 AI 模型
3. 切换不同的风格和参数
4. 多次生成，选择最佳版本

### Q5: 支持哪些音频格式？

**A:**

- 输出：MIDI（旋律）、WAV（完整编曲）

### Q6: 可以离线使用吗？

**A:** 不可以。本软件需要调用在线 AI API，必须保持网络连接。

### Q7: 可以同时使用多个模型吗？

**A:** 可以。你可以在设置中配置多个模型，然后在创作时随时切换使用。配置会自动保存，下次启动时仍然有效。

### Q8: 如何卸载？

**A:**

- 开发模式：直接删除项目目录
- 打包版本：删除可执行文件和 `output/`、`config.json`、`history.json` 文件

### Q9: 配置文件保存在哪里？

**A:**

- `config.json`：所有模型配置和应用设置（在项目根目录）
- `history.json`：创作历史记录（在项目根目录）
- `.env`：应用环境变量（可选，在项目根目录）

### Q10: 如何备份我的配置？

**A:** 备份 `config.json` 文件即可。该文件包含所有模型配置和设置信息。

## 开发说明

### 添加新的 AI 模型

1. 在 `src/ai/` 目录下创建新的客户端模块
2. 实现统一的接口规范（继承 `BaseAIGenerator`）
3. 在 `config_manager.py` 的 `_load_default_config` 方法中添加新模型配置
4. 在 `generator.py` 的 `_create_generator` 方法中添加新模型的创建逻辑

### 项目架构说明

- **配置层**：`config_manager.py` 负责配置的加载、保存和管理
- **业务层**：`generator.py` 负责协调多个 AI 模型
- **界面层**：`main_window.py`、`config_panel.py` 提供用户交互
- **数据层**：`file_manager.py`、`history_manager.py` 处理文件和历史记录

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
