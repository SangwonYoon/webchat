from aiohttp import web
import aiohttp
import time
import redis.asyncio
import json
import asyncio
import logging

logging.basicConfig(
    filename="server.log",
    format="%(asctime)s %(levelname)s:%(message)s", 
    level=logging.INFO
)

routes = web.RouteTableDef()

STOPWORD = "QUIT"
CHANNEL_NAME = "chat-channel"

@routes.get("/ws")
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    id = int((time.time() % 1703000000) * 10000000)

    await info_id(ws, id)

    r = redis.asyncio.Redis(host="redis", port=6379, db=0)
    subscriber = r.pubsub()
    await subscriber.subscribe(CHANNEL_NAME)

    write_task = asyncio.create_task(write_message(ws, id, r))
    read_task = asyncio.create_task(read_message(ws, subscriber))

    await write_task
    await read_task

    logging.info('websocket connection closed')

async def info_id(ws, id):
    info = {"message_type": "info", "content": id}
    await ws.send_json(info)
    logging.info(f"Web Socket Connection Established!, id: {id}")

async def write_message(ws, id, r):
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == STOPWORD:
                break

            chat = {"message_type": "chat", "content": {"sender": id, "message": msg.data}}
            await r.publish(CHANNEL_NAME, json.dumps(chat))

            logging.info(f"publish message from {id} -> {msg.data}")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logging.info(f"ws connection closed with exception {ws.exception()}")

async def read_message(ws, subscriber):
    while not ws.closed:
        result = await subscriber.get_message(ignore_subscribe_messages=True, timeout=None)
        if result is not None:
            chat = json.loads(result["data"])
            try:
                await ws.send_json(chat)
            except ConnectionResetError as e:
                pass

if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)