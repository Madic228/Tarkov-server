import mysql.connector
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import logging

# API ключ и ID канала
API_KEY = "AIzaSyD8WMuLtNjdTHv9KwL4W3AdyhKb_AIjeKg"
CHANNEL_ID = "UC5QGploHhl9_XaxDiHZKamg"


# Время истечения кеша (24 часа)
EXPIRATION_TIME = datetime.timedelta(hours=24)

# Настройка логирования
logging.basicConfig(filename='fillingdb.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.error(f"Ошибка при подключении к базе данных: {str(e)}")
        return None

def get_last_request_time():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT request_time FROM request_time_manager ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        connection.close()
        if result:
            return result[0]  # Вернуть объект datetime напрямую
        else:
            return None
    return None

def fetch_youtube_videos():
    youtube = build("youtube", "v3", developerKey=API_KEY)
    try:
        search_response = youtube.search().list(
            channelId=CHANNEL_ID,
            part="id,snippet",
            order="date",
            maxResults=5
        ).execute()

        videos = []
        for item in search_response["items"]:
            if item["id"]["kind"] == "youtube#video":
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                published_at = item["snippet"]["publishedAt"]
                videos.append((video_id, title, published_at))
        return videos
    except HttpError as e:
        logging.error(f"Ошибка при получении видео с YouTube: {e}")
        return None

def save_videos_to_database(videos):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM videos")
        cursor.executemany(
            "INSERT INTO videos (video_identificator, title, publication_date) VALUES (%s, %s, %s)",
            videos
        )
        connection.commit()
        connection.close()
        logging.info("База данных успешно обновлена.")
    else:
        logging.error("Ошибка при обновлении базы данных: не удалось подключиться.")

def update_request_time():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO request_time_manager (request_time) VALUES (%s)", (now,))
        connection.commit()
        connection.close()

def main():
    last_request_time = get_last_request_time()
    if not last_request_time or datetime.datetime.now() - last_request_time > EXPIRATION_TIME:
        logging.info("Кэш устарел, обновление базы данных...")
        videos = fetch_youtube_videos()
        if videos:
            save_videos_to_database(videos)
            update_request_time()
        else:
            logging.error("Не удалось получить видео с YouTube.")
    else:
        logging.info("Кэш актуален, обновление не требуется.")

if __name__ == "__main__":
    main()