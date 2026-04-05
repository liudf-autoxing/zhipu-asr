#!/usr/bin/env python3
"""
ZhipuAI ASR CLI - Real-time audio transcription tool
Usage: python asr_cli.py --api-key YOUR_KEY [--debug]
       or: ZHIPUAI_API_KEY=xxx python asr_cli.py [--debug]
"""

import io
import signal
import sys
import wave
import os
import argparse

import numpy as np
import sounddevice as sd

from zhipuai import ZhipuAI


# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'
CHUNK_DURATION = 3  # seconds per audio chunk


def parse_args():
    parser = argparse.ArgumentParser(description="ZhipuAI ASR CLI - Real-time audio transcription")
    parser.add_argument("--api-key", "-k", type=str, help="ZhipuAI API key")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug output")
    return parser.parse_args()


class ASRCLI:
    def __init__(self, api_key: str, debug: bool = False):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API key not provided. Use --api-key or set ZHIPUAI_API_KEY")

        self.client = ZhipuAI(api_key=self.api_key)
        self.running = True
        self.history: list[str] = []
        self.debug = debug

        # Setup signal handler for clean exit
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, _signum, _frame):
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
        audio_data = audio_data.flatten()
        if self.debug:
            print(f"[DEBUG] WAV: shape={audio_data.shape}, dtype={audio_data.dtype}, "
                  f"min={audio_data.min()}, max={audio_data.max()}, "
                  f"mean={audio_data.mean():.2f}")
        return audio_data

    def _transcribe_stream(self, wav_bytes: bytes) -> str:
        """Send audio to ASR and return transcription."""
        if self.debug:
            print(f"[DEBUG] Request: wav_bytes={len(wav_bytes)} bytes")

        response = self.client.audio.transcriptions.create(
            file=("audio.wav", wav_bytes, "audio/wav"),
            model="GLM-ASR-2512",
            stream=True
        )

        full_text = ""
        chunk_count = 0
        if self.debug:
            print("[DEBUG] Response chunks:")
        for chunk in response:
            if self.debug:
                print(f"  Chunk {chunk_count}: {chunk}")
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content'):
                    content = delta.content
                    if content:
                        print(content, end="", flush=True)
                        full_text += content
            chunk_count += 1
        if self.debug:
            print(f"[DEBUG] Total chunks received: {chunk_count}")
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
    args = parse_args()
    # Prefer CLI argument, fall back to environment variable
    api_key = args.api_key or os.environ.get("ZHIPUAI_API_KEY")
    try:
        cli = ASRCLI(api_key, debug=args.debug)
        cli.run()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()