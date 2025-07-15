import cv2
import time
import datetime

# URL потока с камеры (замените на свой)
rtsp_url = "rtsp://admin:123456@192.168.6.226/stream=1"

# Папка для сохранения видео (замените на свою)
output_folder = "video_recordings/"

# Создание объекта для захвата видео
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Не удалось открыть поток.")
    exit()

# Определение кодека и параметров записи (пример)
fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Или MJPG, если не работает
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = None

# Функция для создания имени файла
def get_filename():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{output_folder}recording_{timestamp}.mp4"

# Основной цикл записи
try:
    while(True):
        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить кадр.")
            break

        # Инициализация объекта VideoWriter при первом кадре
        if out is None:
            filename = get_filename()
            out = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))

        # Запись кадра
        out.write(frame)
        cv2.imshow('Camera Feed', frame)

        # Выход по нажатию 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Запись остановлена пользователем.")
finally:
    # Освобождение ресурсов
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    print("Программа завершена.")