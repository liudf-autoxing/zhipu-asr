#!/bin/bash
# 后台启动（不占用终端）
cd "$(dirname "$0")"
nohup python zhipu-asr.py "$@" > /dev/null 2>&1 &
