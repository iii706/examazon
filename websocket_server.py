import asyncio
import datetime
import random
import websockets

print(' ========= websocket is going to run =========')


async def livereload(websocket, path):
    while True:
        now = datetime.datetime.utcnow().isoformat() + "U"
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)


start_server = websockets.serve(livereload, "127.0.0.1", 35729)
print(' ========= websocket running =========')
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()