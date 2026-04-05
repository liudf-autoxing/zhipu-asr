# Zhipu ASR CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that records audio from microphone and streams transcription results from ZhipuAI ASR in real-time.

**Architecture:** Single-file CLI that uses sounddevice to continuously record audio in chunks, sends each chunk to ZhipuAI's `/audio/transcriptions` API with streaming enabled, and displays transcriptions with rolling history.

**Tech Stack:** Python 3, sounddevice, numpy, zhipuai SDK

---

## File Structure

```
/home/wurong/workspace/zhipu/
├── asr_cli.py              # Main CLI application
├── requirements.txt        # Dependencies (sounddevice, numpy)
└── docs/superpowers/plans/2026-04-05-zhipu-asr-cli.md  # This plan
```

---

## Task 1: Create requirements.txt

**Files:**
- Create: `/home/wurong/workspace/zhipu/requirements.txt`

- [ ] **Step 1: Create requirements.txt**

```txt
sounddevice
numpy
```

- [ ] **Step 2: Commit**

---

## Task 2: Implement asr_cli.py

**Files:**
- Create: `/home/wurong/workspace/zhipu/asr_cli.py`

- [ ] **Step 1: Write the complete CLI implementation**

```python
#!/usr/bin/env python3
"""
ZhipuAI ASR CLI - Real-time audio transcription tool
Usage: ZHIPUAI_API_KEY=xxx python asr_cli.py
"""

import io
import signal
import sys
import wave
import os
from typing import Optional

import numpy as np
import sounddevice as sd

from zhipuai import ZhipuAI


# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'
CHUNK_DURATION = 3  # seconds per audio chunk


class ASRCLI:
    def __init__(self):
        self.api_key = os.environ.get("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable not set")

        self.client = ZhipuAI(api_key=self.api_key)
        self.running = True
        self.history: list[str] = []

        # Setup signal handler for clean exit
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\n\nStopping...")
        self.running = False

    def _create_wav_bytes(self, audio_data: np.ndarray) -> bytes:
        """Convert numpy audio array to WAV bytes."""
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        buffer.seek(0)
        return buffer.read()

    def _record_chunk(self, duration: int) -> np.ndarray:
        """Record audio chunk from microphone."""
        print(f"Recording {duration}s...", end="", flush=True)
        audio_data = sd.rec(
            frames=duration * SAMPLE_RATE,
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE
        )
        sd.wait()
        print(" done")
        return audio_data.flatten()

    def _transcribe_stream(self, wav_bytes: bytes) -> str:
        """Send audio to ASR and return transcription."""
        response = self.client.audio.transcriptions.create(
            file=("audio.wav", wav_bytes, "audio/wav"),
            model="cosyvoice-v2",
            stream=True
        )

        full_text = ""
        for chunk in response:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content'):
                    content = delta.content
                    if content:
                        print(content, end="", flush=True)
                        full_text += content
        return full_text

    def run(self):
        """Main loop: record, transcribe, display, repeat."""
        print(f"ZhipuAI ASR CLI - Recording {CHUNK_DURATION}s chunks")
        print(f"Sample rate: {SAMPLE_RATE}Hz, Channels: {CHANNELS}, Format: {DTYPE}")
        print("Press Ctrl+C to stop\n")
        print("-" * 50)

        while self.running:
            try:
                # Record audio chunk
                audio_data = self._record_chunk(CHUNK_DURATION)

                # Convert to WAV
                wav_bytes = self._create_wav_bytes(audio_data)

                # Transcribe
                print(f"[{len(self.history) + 1}] ", end="", flush=True)
                text = self._transcribe_stream(wav_bytes)

                if text:
                    self.history.append(text)
                    print()  # Newline after transcription
                else:
                    print(" [no speech detected]")

            except Exception as e:
                print(f"\nError: {e}")
                continue

        # Print final history
        print("\n" + "=" * 50)
        print("TRANSCRIPTION HISTORY:")
        print("=" * 50)
        for i, text in enumerate(self.history, 1):
            print(f"{i}. {text}")


def main():
    try:
        cli = ASRCLI()
        cli.run()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test import**

Run: `python3 -c "import sounddevice, numpy; print('Dependencies OK')"`

- [ ] **Step 3: Test with --help or simple validation**

Run: `python3 asr_cli.py 2>&1 | head -5`
Expected: Error about missing API key (expected behavior)

- [ ] **Step 4: Commit**

---

## Verification

**Test the CLI:**
```bash
pip install -r requirements.txt
ZHIPUAI_API_KEY=your_key python asr_cli.py
```

Speak into your microphone - you should see transcription appear in real-time.

**Expected behavior:**
1. Records 3-second audio chunks
2. Sends each chunk to ZhipuAI ASR API
3. Streams and displays transcription results
4. Maintains history of all transcriptions
5. Clean exit on Ctrl+C with summary
