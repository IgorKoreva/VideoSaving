import cv2
import time
import datetime
import os

# URL потока с камеры (замените на свой)
rtsp_url = "rtsp://admin:123456@192.168.6.226/stream=1"

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

def get_filename():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{output_folder}recording_{timestamp}.mp4"

segment_duration = 40  # секунд
out = None
start_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить кадр.")
            break

        current_time = time.time()

        # Если VideoWriter не инициализирован или прошло 10 секунд — создать новый файл
        if out is None or (current_time - start_time) > segment_duration:
            if out:
                out.release()
            filename = get_filename()
            out = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))
            start_time = current_time

        out.write(frame)
        cv2.imshow('Camera Feed', frame)

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