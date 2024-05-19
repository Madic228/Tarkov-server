from fastapi import FastAPI
import sqlite3
import mysql.connector
import os
from fastapi.responses import FileResponse
from PIL import Image
from io import BytesIO


app = FastAPI()


def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="admin",
            database="tarkov"
        )
        return connection
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {str(e)}")
        return None

def fetch_videos():
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM videos")
            videos = cursor.fetchall()
            connection.close()
            return videos
        else:
            return None
    except Exception as e:
        print(f"Ошибка при выполнении запроса к базе данных: {str(e)}")
        return None

def fetch_request_times():
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM request_time_manager")
            request_times = cursor.fetchall()
            connection.close()
            return request_times
        else:
            return None
    except Exception as e:
        print(f"Ошибка при выполнении запроса к базе данных: {str(e)}")
        return None

@app.get("/videos/")
def get_videos():
    videos = fetch_videos()
    if videos:
        video_list = [{"video_id": video[1], "title": video[2], "publication_date": video[3]} for video in videos]
        return {"videos": video_list}
    else:
        return {"message": "Ошибка при получении видеороликов из базы данных"}

@app.get("/request-times/")
def get_request_times():
    request_times = fetch_request_times()
    if request_times:
        return {"request_times": request_times}
    else:
        return {"message": "Ошибка при получении времен запросов из базы данных"}


# Путь к папке с изображениями
IMAGE_DIRECTORY = "/root/tarkov_api/maps/WoodsMap"

def combine_images(map_image_name, filter_names):
    """
    Объединяет карту и фильтры в одно изображение.

    Args:
        map_image_name: Имя файла карты (например, "карта.png").
        filter_names: Список имен файлов фильтров (например, ["фильтр1.png", "фильтр2.png"]).

    Returns:
        BytesIO: Объединенное изображение в формате BytesIO.
    """
    map_image_path = os.path.join(IMAGE_DIRECTORY, map_image_name)
    map_image = Image.open(map_image_path).convert("RGBA")

    for filter_name in filter_names:
        filter_path = os.path.join(IMAGE_DIRECTORY, filter_name)
        if os.path.exists(filter_path):
            filter_image = Image.open(filter_path).convert("RGBA")
            map_image.paste(filter_image, (0, 0), filter_image)

    # Сохраняем объединенное изображение в BytesIO
    output = BytesIO()
    map_image.save(output, format="PNG")
    output.seek(0)
    return output

@app.get("/images/{map_image_name}/filters/{filter_names}")
async def get_image_with_filters(map_image_name: str, filter_names: str):
    """
    Возвращает объединенное изображение карты с наложенными фильтрами.

    Args:
        map_image_name: Имя файла карты.
        filter_names: Список имен файлов фильтров, разделенных запятыми.

    Returns:
        FileResponse: Объединенное изображение в формате PNG.
    """
    filter_list = filter_names.split(",")
    combined_image = combine_images(map_image_name, filter_list)
    return FileResponse(combined_image, media_type="image/png")
