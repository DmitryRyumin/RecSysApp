from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

app = FastAPI()

# Настройка CORS
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
        print("Полученные данные:", data)

        # Дополнительная логика обработки данных
        return {
            "message": "Данные успешно получены",
            "status": "success",
        }
    except Exception as e:
        # Обработка исключений и возврат ошибки
        return {
            "message": "Произошла ошибка при обработке данных",
            "status": "error",
            "error": str(e)
        }

# Глобальная переменная для хранения экземпляра сервера
server = None

# Функция для запуска сервера
def run_server():
    global server
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()  # Запуск сервера

def stop_server_func():
    global server
    if server:
        server.should_exit = True  # Сигнализируем серверу о необходимости остановки
