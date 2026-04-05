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