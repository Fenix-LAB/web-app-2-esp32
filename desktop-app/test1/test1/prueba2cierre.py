import cv2
import numpy as np
import serial
from collections import Counter
import sys

# --- CONFIGURACIÓN INICIAL ---
try:
    puerto_serial = serial.Serial('COM9', 9600)  # Cambia COM8 según tu puerto
except serial.SerialException:
    print("No se pudo abrir el puerto serial.")
    sys.exit()

cap = cv2.VideoCapture(0)  # Cambia a 0 si usas cámara integrada

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    puerto_serial.close()
    sys.exit()

region_size = 100  # Tamaño del cuadro de detección
ret, frame = cap.read()
h, w, _ = frame.shape
cx, cy = w // 2, h // 2

# --- Función para mover cuadro con mouse ---
def mouse_event(event, x, y, flags, param):
    global cx, cy
    if event == cv2.EVENT_LBUTTONDOWN:
        cx, cy = x, y

cv2.namedWindow("Color Detector")
cv2.setMouseCallback("Color Detector", mouse_event)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Coordenadas del cuadro
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

        # Imprimir y enviar por serial
        print(f"{r},{g},{b}")
        try:
            puerto_serial.write(f"{r},{g},{b}\n".encode())
        except serial.SerialException:
            pass

        # Dibujar cuadro y mostrar
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{r},{g},{b}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Color Detector", frame)

        # Salir con ESC o cerrar ventana
        key = cv2.waitKey(1)
        if key == 27 or cv2.getWindowProperty("Color Detector", cv2.WND_PROP_VISIBLE) < 1:
            break

except KeyboardInterrupt:
    print("Interrumpido por el usuario")

finally:
    # Cierre limpio
    cap.release()
    cv2.destroyAllWindows()
    if puerto_serial.is_open:
        puerto_serial.close()
