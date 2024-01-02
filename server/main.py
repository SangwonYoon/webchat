import asyncio
import json
import logging
import os
import socket
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

import aiohttp
import redis.asyncio
from aiohttp import web

routes = web.RouteTableDef()

STOPWORD = "QUIT"
CHANNEL_NAME = "chat-channel"
CPU_COUNT = cpu_count()

logging.basicConfig(
    filename=f"server.log",
    format="%(asctime)s Process %(process)d:%(message)s", 
    level=logging.INFO
)

def make_socket(host, port, reuseport):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if reuseport:
        SO_REUSEPORT = 15
        sock.setsockopt(socket.SOL_SOCKET, SO_REUSEPORT, 1)
    sock.bind((host, port))
    return sock

async def get_nickname(ws):
    msg = await ws.receive()
    return msg.data

async def info_id(ws, id):
    info = {"message_type": "info", "content": id}
    await ws.send_json(info)
    logging.info(f"websocket connection established!, id: {id}")

async def notify_enterance(nickname, r):
    info = {"message_type": "enterance", "content": nickname}
    await r.publish(CHANNEL_NAME, json.dumps(info))

    logging.info(f"publish enterance message from {nickname}")

async def write_message(ws, id, nickname, r):
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == STOPWORD:
                break

            chat = {"message_type": "chat", "content": {"sender": id, "sender_nickname": nickname, "message": msg.data}}
            await r.publish(CHANNEL_NAME, json.dumps(chat))

            logging.info(f"publish message from {id} -> {msg.data}")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logging.info(f"ws connection closed with exception {ws.exception()}")

    info = {"message_type": "exit", "content": nickname}
    await r.publish(CHANNEL_NAME, json.dumps(info))

    logging.info(f"publish exit message from {nickname}")

async def read_message(ws, subscriber):
    while not ws.closed:
        result = await subscriber.get_message(ignore_subscribe_messages=True, timeout=None)
        if result is not None:
            chat = json.loads(result["data"])
            try:
                await ws.send_json(chat)
            except ConnectionResetError as e:
                pass

@routes.get("/ws")
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    id = int((time.time() % 1703000000) * 10000000)

    nickname = await get_nickname(ws)
    logging.info(f"{nickname=}")

    await info_id(ws, id)

    REDIS_HOST_NAME = "redis"
    r = redis.asyncio.Redis(host=REDIS_HOST_NAME, port=6379, db=0)
    subscriber = r.pubsub()
    await subscriber.subscribe(CHANNEL_NAME)

    await notify_enterance(nickname, r)

    write_task = asyncio.create_task(write_message(ws, id, nickname, r))
    read_task = asyncio.create_task(read_message(ws, subscriber))

    await write_task
    await read_task

    logging.info("websocket connection closed")

async def start_server():
    host = "0.0.0.0"
    port = 8080
    reuseport = True

    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    sock = make_socket(host, port, reuseport)
    server = web.SockSite(runner, sock)
    await server.start()
    logging.info(f"server started")
    return server, app, runner

async def finalize(server, app, runner):
    sock = server.sockets[0]
    app.loop.remove_reader(sock.fileno())
    sock.close()

    await runner.cleanup()
    server.close()
    await server.wait_closed()
    await app.finish()

def main():
    loop = asyncio.get_event_loop()
    server, app, runner = loop.run_until_complete(start_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete((finalize(server, app, runner)))

if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        for _ in range(0, CPU_COUNT):
            executor.submit(main)