from __future__ import annotations

from typing import Annotated
from fastapi import FastAPI, WebSocket, Header, WebSocketDisconnect


# uvicorn main:app --reload --port 8100

app = FastAPI()

def print_msg(msg):
    print(msg)

# server_program()
@app.websocket("/ws")
async def websocket(
        websocket: WebSocket,
        # user_agent,
        custom_header: Annotated[str | None, Header(alias="X-Custom-Header")] = None):
    print(custom_header)
    await websocket.accept()
    await websocket.send_json({"msg": custom_header})

    data = await websocket.receive_text()
    print(data)


# await websocket.close()


# from typing import Annotated
# from fastapi import FastAPI, WebSocket, Header, WebSocketDisconnect
#
# app = FastAPI()


# @app.websocket("/ws")
# async def websocket_endpoint(
#         websocket: WebSocket,
#         user_agent: Annotated[str | None, Header(None)] = None,  # Accessing the User-Agent header
#         custom_header: Annotated[str | None, Header(alias="X-Custom-Header")] = None  # Accessing a custom header
# ):
#     await websocket.accept()
#     try:
#         if user_agent:
#             await websocket.send_text(f"User-Agent: {user_agent}")
#         if custom_header:
#             await websocket.send_text(f"Custom Header: {custom_header}")
#
#         while True:
#             data = await websocket.receive_text()
#             await websocket.send_text(f"Message received: {data}")
#     except WebSocketDisconnect:
#         print("Client disconnected")