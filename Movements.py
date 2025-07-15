import cv2
import time
import datetime
import os
import numpy as np

# URL потока с камеры (замените на свой)
rtsp_url = "rtsp://admin:@192.168.7.102/stream=0"

# Папка для сохранения видео (замените на свою)
output_folder = "video_recordings/"
os.makedirs(output_folder, exist_ok=True)

# Создание объекта для захвата видео
cap = cv2.VideoCapture(rtsp_url)
if not cap.isOpened():
    print("Не удалось открыть поток.")
    exit()

# Определение кодека и параметров записи
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 20.0  # запасной вариант

def get_filename():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{output_folder}recording_{timestamp}.mp4"

motion_threshold = 5000  # порог по количеству изменившихся пикселей
segment_duration = 60  # секунд - максимальная длительность сегмента

prev_gray = None
out = None
recording = False
start_time = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить кадр.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)  # размываем для снижения шума

        if prev_gray is None:
            prev_gray = gray
            continue

        # Вычисляем разницу между текущим и предыдущим кадрами
        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        motion_count = cv2.countNonZero(thresh)

        if motion_count > motion_threshold:
            if not recording:
                print(f"Движение обнаружено. Начинаю запись: {datetime.datetime.now()}")
                filename = get_filename()
                out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
                start_time = time.time()
                recording = True
            else:
                # Проверяем длительность записи
                if (time.time() - start_time) > segment_duration:
                    out.release()
                    filename = get_filename()
                    out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
                    start_time = time.time()

            out.write(frame)
        else:
            # Если движение отсутствует, но запись шла — завершаем файл
            if recording:
                print(f"Движение прекратилось. Останавливаю запись: {datetime.datetime.now()}")
                out.release()
                out = None
                recording = False

        prev_gray = gray

        cv2.imshow('Camera Feed', frame)
        # cv2.imshow('Thresh', thresh)  # можно раскомментировать для отладки

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Запись остановлена пользователем.")
finally:
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    print("Программа завершена.")