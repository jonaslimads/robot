
# For test only

import asyncio
import websockets
import time

async def hello():
    uri = "ws://192.168.0.4:8765/ws/microphone"
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

        time.sleep(30)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(hello())