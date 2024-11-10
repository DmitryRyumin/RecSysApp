"""
File: server.py
Author: Dmitry Ryumin
Description: Server for the application.
License: MIT License
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.event_handlers.db_handler import save_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/submit")
async def receive_data(request: Request):
    try:
        data = await request.json()
        # print("Полученные данные:", data)

        # Сохранение данных с использованием модуля db_handler
        if save_data(data):
            return {
                "message": "Данные успешно получены и сохранены",
                "status": "success",
            }
        else:
            return {
                "message": "Ошибка при сохранении данных",
                "status": "error",
            }
    except Exception as e:
        # Обработка исключений и возврат ошибки
        return {
            "message": "Произошла ошибка при обработке данных",
            "status": "error",
            "error": str(e),
        }

server = None

def run_server():
    global server
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()


def stop_server_func():
    global server
    if server:
        server.should_exit = True
