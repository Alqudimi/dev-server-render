from fastapi import WebSocket
import asyncio
import subprocess
from typing import Optional

class TerminalWebSocket:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.process: Optional[subprocess.Popen] = None

    async def connect(self):
        await self.websocket.accept()
        self.process = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

    async def receive_commands(self):
        while True:
            try:
                data = await self.websocket.receive_text()
                if self.process and self.process.stdin:
                    self.process.stdin.write(data + "\n")
                    self.process.stdin.flush()
            except Exception as e:
                print(f"Error receiving command: {e}")
                break

    async def send_output(self):
        while True:
            if self.process and self.process.stdout:
                output = self.process.stdout.readline()
                if output:
                    await self.websocket.send_text(output)
                else:
                    await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.1)

    async def disconnect(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        await self.websocket.close()
