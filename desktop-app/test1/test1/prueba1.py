import cv2
import numpy as np
import serial
from collections import Counter

# --- CONFIGURACIÓN INICIAL ---
puerto_serial = serial.Serial('COM8', 9600)  # Cambia COM3 según tu caso
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

# Tamaño del cuadro de detección en píxeles (ajusta para que represente ~9x9 cm)
region_size = 100

# Posición inicial del cuadro (centro de la pantalla)
ret, frame = cap.read()
h, w, _ = frame.shape
cx, cy = w // 2, h // 2

# --- FUNCIONES PARA MOVER CON MOUSE ---
def mouse_event(event, x, y, flags, param):
    global cx, cy
    if event == cv2.EVENT_LBUTTONDOWN:
        cx, cy = x, y

cv2.namedWindow("Color Detector")
cv2.setMouseCallback("Color Detector", mouse_event)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Coordenadas del cuadro
    half = region_size // 2
    x1, y1 = max(cx - half, 0), max(cy - half, 0)
    x2, y2 = min(cx + half, w), min(cy + half, h)

    # Extraer la región
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        continue

    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    reshaped = roi_rgb.reshape(-1, 3)
    colors, counts = np.unique(reshaped, axis=0, return_counts=True)
    dominant_color = colors[counts.argmax()]
    r, g, b = dominant_color

    # Imprimir y enviar por serial
    print(f"{r},{g},{b}")
    try:
        puerto_serial.write(f"{r},{g},{b}\n".encode())
    except:
        pass

    # Dibujar cuadro en pantalla
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(frame, f"{r},{g},{b}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Mostrar video
    cv2.imshow("Color Detector", frame)

    # Salir con ESC
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
puerto_serial.close()
