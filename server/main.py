from aiohttp import web
import aiohttp
import time

routes = web.RouteTableDef()
ws_clients = {}

STOPWORD = "QUIT"

@routes.get("/ws")
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    id = int((time.time() % 1703000000) * 10000000)

    ws_clients[id] = ws
    info = {"message_type": "info", "content": id}
    await ws.send_json(info)
    print(f"Web Socket Connection Established!, id: {id}")

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == STOPWORD:
                break

            chat = {"message_type": "chat", "content": {"sender": id, "message": msg.data}}

            for ws_client in ws_clients.values():
                try:
                    chat = {"message_type": "chat", "content": {"sender": id, "message": msg.data}}
                    await ws_client.send_json(chat)
                except ConnectionResetError as e:
                    pass
            print(id, msg.data)
            print(f"{ws_clients=}")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %ws.exception())

    ws_clients.pop(id)

    print('websocket connection closed')

if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)