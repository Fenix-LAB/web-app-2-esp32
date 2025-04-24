import cv2
import numpy as np
import serial
import sys
import time
import csv
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
try:
    puerto_serial = serial.Serial('COM8', 9600)  # Cambia COM8 según tu puerto
except serial.SerialException:
    print("No se pudo abrir el puerto serial.")
    sys.exit()

cap = cv2.VideoCapture(0)  # 0 si es cámara integrada

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    puerto_serial.close()
    sys.exit()

region_size = 100
ret, frame = cap.read()
h, w, _ = frame.shape
cx, cy = w // 2, h // 2

# Tiempo del último envío
ultimo_envio = time.time()

# --- Abrir archivo CSV para guardar datos ---
archivo_csv = open("rgb_log.csv", mode="a", newline="")
escritor_csv = csv.writer(archivo_csv)

# Escribir encabezado solo si el archivo está vacío
if archivo_csv.tell() == 0:
    escritor_csv.writerow(["Hora", "R", "G", "B"])

# Función para mover el cuadro con el mouse
def mouse_event(event, x, y, flags, param):
    global cx, cy
    if event == cv2.EVENT_LBUTTONDOWN:
        cx, cy = x, y

cv2.namedWindow("Color Detector")
cv2.setMouseCallback("Color Detector", mouse_event)

def mejorar_colores(frame_bgr):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 10)
    v = cv2.add(v, 40)
    hsv_mejorado = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv_mejorado, cv2.COLOR_HSV2BGR)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = mejorar_colores(frame)

        half = region_size // 2
        x1, y1 = max(cx - half, 0), max(cy - half, 0)
        x2, y2 = min(cx + half, w), min(cy + half, h)

        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue

        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        reshaped = roi_rgb.reshape(-1, 3)
        colors, counts = np.unique(reshaped, axis=0, return_counts=True)
        dominant_color = colors[counts.argmax()]
        r, g, b = dominant_color

        # Enviar y guardar cada 2 segundos
        tiempo_actual = time.time()
        if tiempo_actual - ultimo_envio >= 2:
            mensaje = f"{r},{g},{b}"
            hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{hora_actual}, {mensaje}")
            
            try:
                puerto_serial.write((mensaje + "\n").encode())
            except serial.SerialException:
                pass

            escritor_csv.writerow([hora_actual, r, g, b])
            archivo_csv.flush()  # Asegura que se guarden los datos
            ultimo_envio = tiempo_actual

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{r},{g},{b}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Color Detector", frame)

        key = cv2.waitKey(1)
        if key == 27 or cv2.getWindowProperty("Color Detector", cv2.WND_PROP_VISIBLE) < 1:
            break

except KeyboardInterrupt:
    print("Interrumpido por el usuario")

finally:
    cap.release()
    cv2.destroyAllWindows()
    if puerto_serial.is_open:
        puerto_serial.close()
    archivo_csv.close()
