from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Query
import mysql.connector
import os
from PIL import Image
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
import logging
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import FileResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

def log_message(message):
    logging.info(message)

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="admin",
            database="tarkov"
        )
        log_message("Успешное подключение к базе данных")
        return connection
    except Exception as e:
        log_message(f"Ошибка при подключении к базе данных: {str(e)}")
        return None

def fetch_videos():
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM videos")
            videos = cursor.fetchall()
            connection.close()
            log_message(f"Получено {len(videos)} видео из базы данных")
            return videos
        else:
            return None
    except Exception as e:
        log_message(f"Ошибка при выполнении запроса к базе данных: {str(e)}")
        return None

def fetch_request_times():
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM request_time_manager")
            request_times = cursor.fetchall()
            connection.close()
            log_message(f"Получено {len(request_times)} времен запросов из базы данных")
            return request_times
        else:
            return None
    except Exception as e:
        log_message(f"Ошибка при выполнении запроса к базе данных: {str(e)}")
        return None

@app.get("/videos/")
def get_videos():
    videos = fetch_videos()
    if videos:
        video_list = [{"video_id": video[1], "title": video[2], "publication_date": video[3]} for video in videos]
        log_message("Получен список видеороликов")
        return {"videos": video_list}
    else:
        return {"message": "Ошибка при получении видеороликов из базы данных"}

@app.get("/request-times/")
def get_request_times():
    request_times = fetch_request_times()
    if request_times:
        log_message("Получены запросы времени")
        return {"request_times": request_times}
    else:
        return {"message": "Ошибка при получении времен запросов из базы данных"}

# Путь к папке с изображениями
IMAGE_DIRECTORY = "/root/tarkov_api/maps/WoodsMap"

@app.get("/images/{image_name}")
async def get_image(image_name: str):
    image_path = os.path.join(IMAGE_DIRECTORY, image_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    else:
        return {"message": "Изображение не найдено"}
