# ZhipuAI ASR 输入法

Linux 语音输入法——按住右Ctrl说话，识别结果自动输入到焦点窗口。

## 功能

- 按住 **右Ctrl** 开始录音
- 松开 **右Ctrl** 发送识别，结果自动输入
- 剪贴板 + `Ctrl+Shift+V` 粘贴（Wayland/X11 兼容）

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python asr_cli.py -k YOUR_API_KEY
```

或设置环境变量：

```bash
export ZHIPUAI_API_KEY=your_key
python asr_cli.py
```

## 选项

- `-k, --api-key` API密钥
- `-d, --debug` 调试模式

## 依赖

- sounddevice
- numpy
- pynput（按键监听，无需root）
- pyperclip（剪贴板）
- pyautogui（模拟按键）
