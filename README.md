# zhipu-asr

Linux 语音输入法——基于智谱 AI GLM-ASR API，按住右 Ctrl 说话，识别结果自动输入到焦点窗口。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 获取 API Key

前往 [智谱 AI 开放平台](https://open.bigmodel.cn/) 注册并获取 API Key。

### 3. 运行

```bash
python zhipu_tray.py --api-key YOUR_API_KEY
```

或设置环境变量：

```bash
export ZHIPUAI_API_KEY=your_key
python zhipu_tray.py
```

### 4. 使用

- **按住右 Ctrl** → 开始录音
- **松开右 Ctrl** → 停止录音，识别结果自动输入到焦点窗口

## 快捷键

| 按键 | 功能 |
|------|------|
| 右 Ctrl（按住） | 开始录音 |
| 右 Ctrl（松开） | 停止录音并识别 |

## 配置

首次运行后，配置保存在 `~/.config/zhipu/config.yaml`。

可用配置项：

```yaml
hotwords:
  - Python
  - Linux

prompt: "用户正在讨论技术问题"
```

## 命令行选项

- `-k, --api-key` - 智谱 AI API Key

## 项目结构

```
zhipu-asr/
├── zhipu_tray.py      # 主入口（系统托盘 + 主窗口）
├── asr_engine.py      # ASR 核心引擎
├── ui/
│   ├── main_window.py # 主窗口 UI
│   └── styles.py      # 样式表
├── assets/
│   └── icons/         # 图标资源
├── config.yaml.example # 配置示例
├── requirements.txt
└── LICENSE            # MIT License
```

## License

MIT
