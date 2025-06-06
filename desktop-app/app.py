from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo   # Modulo Serial de PyQt5
from PyQt5.QtCore import *                                    # Modulo PyQt5 para intarfaces graficas
from gui_design import *
from PyQt5.QtGui import *
import time
from datetime import datetime
import csv
import pyqtgraph as pg
import numpy as np
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import os
import shutil

from PyQt5.QtCore import QThread, pyqtSignal, QDateTime

class TimerThread(QThread):
    update_time = pyqtSignal(str)  # Señal para actualizar el tiempo en el QLabel

    def __init__(self, label, format="mm:ss"):
        super().__init__()
        self.label = label  # QLabel que mostrará el tiempo
        self.format = format  # Formato de tiempo: "mm:ss" o "hh:mm:ss"
        self.running = False  # Estado del cronómetro
        self.start_time = None  # Tiempo de inicio
        self.region_size = 100  

    def run(self):
        self.running = True
        self.start_time = QDateTime.currentDateTime()  # Guarda el tiempo de inicio

        while self.running:
            current_time = QDateTime.currentDateTime()  # Obtiene el tiempo actual
            elapsed_time = self.start_time.msecsTo(current_time)  # Calcula el tiempo transcurrido en milisegundos

            # Convierte el tiempo transcurrido a segundos
            seconds = elapsed_time // 1000

            # Formatea el tiempo según el formato especificado
            if self.format == "mm:ss":
                minutes = seconds // 60
                seconds = seconds % 60
                time_str = f"{minutes:02}:{seconds:02}"
            elif self.format == "hh:mm:ss":
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

            # Emite la señal para actualizar el QLabel
            self.update_time.emit(time_str)

            self.msleep(1000)  # Espera 1 segundo antes de la siguiente actualización

    def stop(self):
        """
        Detiene el cronómetro.
        """
        self.running = False
        self.wait()  # Espera a que el hilo termine

    def reset(self):
        """
        Reinicia el cronómetro.
        """
        self.start_time = QDateTime.currentDateTime()

class CameraThread(QThread):
    frame_ready = pyqtSignal(QPixmap)
    dominant_color_changed = pyqtSignal(tuple)  # Nueva señal para el color dominante (R,G,B)
    
    def __init__(self, camera_index=0, region_size=100):
        super().__init__()
        self.camera_index = camera_index
        self.region_size = region_size  # Tamaño del área de análisis
        self.running = False
        self.current_frame = None
        self.dominant_color = (0, 0, 0)  # (R, G, B)
        self.mutex = QMutex()
        self.cap = None
        
    def set_camera(self, index):
        """Cambia la cámara de manera segura"""
        self.mutex.lock()
        
        try:
            # 1. Liberar la cámara actual si existe
            if self.cap is not None:
                self.cap.release()
            
            # 2. Intentar abrir la nueva cámara
            self.cap = cv2.VideoCapture(index)
            if not self.cap.isOpened():
                raise ValueError(f"No se pudo abrir la cámara con índice {index}")
            
            self.camera_index = index
            print(f"Cámara cambiada a índice {index} correctamente")
            
        except Exception as e:
            print(f"Error al cambiar cámara: {str(e)}")
            # Recuperar cámara anterior si es posible
            if hasattr(self, 'camera_index'):
                self.cap = cv2.VideoCapture(self.camera_index)
        
        finally:
            self.mutex.unlock()

    def run(self):
        self.running = True
        self.cap = cv2.VideoCapture(self.camera_index)
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Procesamiento del frame
            processed_frame = self.enhance_colors(frame)
            
            # Definir región de interés (centrada)
            h, w, _ = processed_frame.shape
            cx, cy = w // 2, h // 2
            half = self.region_size // 2
            x1, y1 = max(cx - half, 0), max(cy - half, 0)
            x2, y2 = min(cx + half, w), min(cy + half, h)
            roi = processed_frame[y1:y2, x1:x2]
            
            # Calcular color dominante si hay ROI válida
            if roi.size > 0:
                self.calculate_dominant_color(roi)
                # Dibujar rectángulo en el frame
                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Guardar frame actual y emitir
            self.mutex.lock()
            self.current_frame = processed_frame.copy()
            self.mutex.unlock()
            
            # Convertir a QPixmap y emitir
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(QPixmap.fromImage(qt_image))
    
    def enhance_colors(self, frame):
        """Mejora los colores del frame (similar al código original)"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.add(s, 10)
        v = cv2.add(v, 40)
        hsv_enhanced = cv2.merge([h, s, v])
        return cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
    
    def calculate_dominant_color(self, roi):
        """Calcula el color dominante en la ROI (BGR -> RGB)"""
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        reshaped = roi_rgb.reshape(-1, 3)
        colors, counts = np.unique(reshaped, axis=0, return_counts=True)
        bgr_dominant = colors[counts.argmax()]
        
        # Convertir a RGB y guardar
        self.dominant_color = (bgr_dominant[2], bgr_dominant[1], bgr_dominant[0])
        self.dominant_color_changed.emit(self.dominant_color)
    
    def get_dominant_color(self):
        """Retorna el último color dominante calculado (R, G, B)"""
        self.mutex.lock()
        color = self.dominant_color
        self.mutex.unlock()
        return color
    
    def stop(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
        self.wait()

#Clase de la ventana heredada de la interfaz "gui_design.py"
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    # Se define le contructor con todos los atributos necesarios y asociacion de metodos
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        self.stage_1 = False
        self.stage_2 = False
        self.stage_3 = False
        self.stage_4 = False
        self.stage_5 = False
        self.file_name = None
        self.save_button = False
        self.file_name = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

        # Usamos la funcion QPoint() para guardar la posicion del mouse
        self.click_position = QPoint()
        # self.btn_menu.clicked.connect(self.mover_menu)

        # Se configura la ventana asociando los eventos con metodos
        # self.btn_normal.hide()
        self.btn_min.clicked.connect(lambda: self.showMinimized())
        self.btn_cerrar.clicked.connect(self.control_btn_cerrar)
        # self.btn_normal.clicked.connect(self.control_btn_normal)
        # self.btn_max.clicked.connect(self.control_btn_maximizar)
        self.btn_iniciar_1.clicked.connect(self.start_stage_1)
        # self.btn_iniciar_2.clicked.connect(self.start_stage_2) # Ya no existe esta etapa
        self.btn_iniciar_3.clicked.connect(self.start_stage_3)
        # self.btn_iniciar_4.clicked.connect(self.start_stage_4) # Ya no existe esta etapa
        self.btn_iniciar_5.clicked.connect(self.start_stage_5)
        self.btn_guardar.clicked.connect(self.save_button_clicked)


        # Se elimina la barra de titulo por default
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Size grip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        # Movimiento de la ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        # Control connect
        self.serial = QSerialPort()
        self.btn_actualizar.clicked.connect(self.read_ports)
        self.btn_conectar.clicked.connect(self.serial_conect)
        self.btn_desconectar.clicked.connect(self.serial_desconect)

        # Graficas
        self.t1_x = list(np.linspace(0, 540, 540))
        self.t1_y = list(np.linspace(0, 0, 540))

        self.t2_x = list(np.linspace(0, 540, 540))
        self.t2_y = list(np.linspace(0, 0, 540))

        self.h1_x = list(np.linspace(0, 540, 540))
        self.h1_y = list(np.linspace(0, 0, 540))

        self.r1_y = list(np.linspace(0, 0, 540))
        self.r1_x = list(np.linspace(0, 540, 540))

        # Creacion de la grafica 1
        pg.setConfigOption('background', '#ebfeff')
        pg.setConfigOption('foreground', '#000000')
        self.plt = pg.PlotWidget()
        self.graph_1.addWidget(self.plt)

        # pg.setConfigOption('background', '#ebfeff')
        # pg.setConfigOption('foreground', '#000000')
        # self.plt2 = pg.PlotWidget()
        # self.graph_2.addWidget(self.plt2)

        pg.setConfigOption('background', '#ebfeff')
        pg.setConfigOption('foreground', '#000000')
        self.plt3 = pg.PlotWidget()
        # self.graph_3.addWidget(self.plt3)

        # Asociacion de metodos
        self.serial.readyRead.connect(self.read_data)
        self.read_ports()

        # self.set_progressbar_2_zero()
        self.disable_all_start_buttons()
        self.disable_save_button()

        # enable first button
        self.enable_button(self.btn_iniciar_1)
        self.disable_button(self.btn_desconectar)

        # Inicializar el hilo de la cámara
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_camera_view)
        
        # Configurar el combo box con las cámaras disponibles
        # self.setup_camera_combobox()
        self.comboBox_camara.addItems(["0", "1", "2"])
        # self.setup_camera_combobox()
        self.comboBox_camara.currentIndexChanged.connect(self.change_camera)
        
        # Iniciar la cámara
        self.camera_thread.start()

    # def set_progressbar_2_zero(self):
    #     """
    #     Metodo para poner en 0 todas las barras de progreso
        
    #     """
    #     self.prog_1.setValue(0)
    #     # self.prog_2.setValue(0)
    #     self.prog_3.setValue(0)
    #     # self.prog_4.setValue(0)
    #     # self.prog_5.setValue(0)

    def disable_all_start_buttons(self):
        """
        Metodo para deshabilitar todos los botones de inicio
        
        """
        style_grayed_out = """QPushButton{
        background-color: rgb(84,111,150);
        }
        QPushButton:hover{
        background-color: rgb(84,111,150);
        }
        """

        self.btn_iniciar_1.setEnabled(False)
        # self.btn_iniciar_2.setEnabled(False)
        self.btn_iniciar_3.setEnabled(False)
        # self.btn_iniciar_4.setEnabled(False)
        self.btn_iniciar_5.setEnabled(False)

        # Now change style to grayed out
        self.btn_iniciar_1.setStyleSheet(style_grayed_out)
        # self.btn_iniciar_2.setStyleSheet(style_grayed_out)
        self.btn_iniciar_3.setStyleSheet(style_grayed_out)
        # self.btn_iniciar_4.setStyleSheet(style_grayed_out)
        self.btn_iniciar_5.setStyleSheet(style_grayed_out)
    
    def disable_save_button(self):
        """
        Metodo para deshabilitar el boton de guardar
        
        """
        style_grayed_out = """QPushButton{
        background-color: rgb(84,111,150);
        }
        QPushButton:hover{
        background-color: rgb(84,111,150);
        }
        """

        self.btn_guardar.setEnabled(False)
        self.btn_guardar.setStyleSheet(style_grayed_out)

    def enable_button(self, button):
        """
        Metodo para habilitar el boton de inicio
        
        """
        style = """QPushButton{
        background-color: rgb(84,111,236);
        }
        QPushButton:hover{
        background-color: rgb(39,74,233);
        }
        """

        button.setEnabled(True)
        button.setStyleSheet(style)

    def disable_button(self, button):
        """
        Metodo para deshabilitar el boton de inicio
        
        """
        style_grayed_out = """QPushButton{
        background-color: rgb(84,111,150);
        }
        QPushButton:hover{
        background-color: rgb(84,111,150);
        }
        """

        button.setEnabled(False)
        button.setStyleSheet(style_grayed_out)

    def change_button_text(self, button, text):
        """
        Metodo para cambiar el texto del boton
        
        """
        button.setText(text)

    def start_stage_1(self):
        """
        Metodo para iniciar la captura de datos
        
        """

        self.timer_stage_1 = TimerThread(self.timer_1, format="mm:ss")
        self.timer_stage_1.update_time.connect(self.timer_1.setText)
        
        self.timer_total = TimerThread(self.timer_4, format="hh:mm:ss")
        self.timer_total.update_time.connect(self.timer_4.setText)

        self.stage_1 = True
        self.enable_button(self.btn_iniciar_3)
        self.disable_button(self.btn_iniciar_1)
        self.change_button_text(self.btn_iniciar_1, "...")
        # self.start_progressbar_1()
        self.timer_stage_1.start()  # Inicia el cronómetro
        self.timer_total.start()

        self.start_time_stage1 = datetime.now()

        self.create_csv()


    # def start_stage_2(self):
    #     """
    #     Metodo para iniciar la captura de datos
        
    #     """
    #     self.stage_2 = True
    #     self.enable_button(self.btn_iniciar_3)
    #     # self.start_progressbar_2()
    #     self.disable_button(self.btn_iniciar_2)
    #     self.change_button_text(self.btn_iniciar_1, "Listo")
    #     self.change_button_text(self.btn_iniciar_2, "...")
    #     self.start_progressbar_2()

    #     self.start_time_stage2 = datetime.now()

    def start_stage_3(self):
        """
        Metodo para iniciar la captura de datos
        
        """
        self.timer_stage_3 = TimerThread(self.timer_2, format="mm:ss")
        self.timer_stage_3.update_time.connect(self.timer_2.setText)

        self.stage_3 = True
        self.enable_button(self.btn_iniciar_5)
        self.disable_button(self.btn_iniciar_3)
        self.change_button_text(self.btn_iniciar_1, "Listo")
        self.change_button_text(self.btn_iniciar_3, "...")
        # self.start_progressbar_3()
        self.timer_stage_3.start()
        self.timer_stage_1.stop()


        self.start_time_stage3 = datetime.now()

    # def start_stage_4(self):
    #     """
    #     Metodo para iniciar la captura de datos
        
    #     """
    #     self.stage_4 = True
    #     self.enable_button(self.btn_iniciar_5)
    #     self.disable_button(self.btn_iniciar_4)
    #     self.change_button_text(self.btn_iniciar_3, "Listo")
    #     self.change_button_text(self.btn_iniciar_4, "...")
    #     self.start_progressbar_4()

    #     self.start_time_stage4 = datetime.now()

    def start_stage_5(self):
        """
        Metodo para iniciar la captura de datos
        
        """
        self.timer_stage_5 = TimerThread(self.timer_3, format="mm:ss")
        self.timer_stage_5.update_time.connect(self.timer_3.setText)

        self.stage_5 = True
        self.enable_button(self.btn_guardar)
        self.disable_button(self.btn_iniciar_5)
        self.change_button_text(self.btn_iniciar_3, "Listo")
        self.change_button_text(self.btn_iniciar_5, "...")
        # self.start_progressbar_5()
        self.timer_stage_5.start()
        self.timer_stage_3.stop()

        self.start_time_stage5 = datetime.now()


    # def start_progressbar_1(self):
    #     """
    #     Metodo para iniciar la barra de progreso
    #     Solo es visual, la barra de progreso no tiene ninguna funcion
    #     Avanzara de de forma constante hasta llegar al 100%
    #     Si se presiona el siguiente boton de inicio, la barra de progreso llegara el 100%
        
    #     """
    #     self.prog_1.setValue(0)
    #     self.progress_thread_1 = ProgressBarThread(self.prog_1, lambda: self.stage_2)
    #     self.progress_thread_1.update_progress.connect(self.prog_1.setValue)
    #     self.progress_thread_1.start()

    # def start_progressbar_2(self):
    #     """
    #     Metodo para iniciar la barra de progreso
    #     """

    #     self.prog_2.setValue(0)
        
    #     self.progress_thread_2 = ProgressBarThread(self.prog_2, lambda: self.stage_3)
    #     self.progress_thread_2.update_progress.connect(self.prog_2.setValue)
    #     self.progress_thread_2.start()

    # def start_progressbar_3(self):
    #     """
    #     Metodo para iniciar la barra de progreso
    #     """

    #     self.prog_3.setValue(0)
        
    #     self.progress_thread_3 = ProgressBarThread(self.prog_3, lambda: self.stage_4)
    #     self.progress_thread_3.update_progress.connect(self.prog_3.setValue)
    #     self.progress_thread_3.start()

    # def start_progressbar_4(self):
    #     """
    #     Metodo para iniciar la barra de progreso
    #     """

    #     self.prog_4.setValue(0)
        
    #     self.progress_thread_4 = ProgressBarThread(self.prog_4, lambda: self.stage_5)
    #     self.progress_thread_4.update_progress.connect(self.prog_4.setValue)
    #     self.progress_thread_4.start()
    
    # def start_progressbar_5(self):
    #     """
    #     Metodo para iniciar la barra de progreso
    #     """

    #     self.prog_5.setValue(0)
        
    #     self.progress_thread_5 = ProgressBarThread(self.prog_5, lambda: self.save_button)
    #     self.progress_thread_5.update_progress.connect(self.prog_5.setValue)
    #     self.progress_thread_5.start()


    def save_button_clicked(self):
        """
        Metodo para guardar los datos en un archivo CSV
        """

        self.save_button = True
        self.change_button_text(self.btn_iniciar_5, "Listo")
        self.timer_stage_5.stop()
        self.timer_total.stop()
        # self.change_button_text(self.btn_guardar, "Guardando...")
        # time.sleep(5)
        self.create_end_csv()
        time.sleep(1)  # Espera para que el usuario vea el mensaje de guardado
        df = self.load_and_process_data(self.file_name)
        fases = self.identify_phases(df)
        eventos = self.identify_key_events(df)
        rgb = self.analyze_rgb(df)
        self.create_pdf_report(df, eventos, fases, rgb, self.file_name.replace('.csv', '.pdf'))

        self.move_to_folder(f"Analisis_Cafe_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        # self.create_graph_for_tostado()
        self.change_button_text(self.btn_guardar, "Guardado")


        self.disable_save_button()

    def move_to_folder(self, folder):
        """
        Metodo para mover el archivo CSV y el pdf a una carpeta especifica
        """
        

        # Verifica si la carpeta existe, si no, la crea
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Mueve el archivo CSV
        csv_file_path = self.file_name
        if os.path.exists(csv_file_path):
            shutil.move(csv_file_path, os.path.join(folder, os.path.basename(csv_file_path)))

        # Mueve el archivo PDF
        pdf_file_path = self.file_name.replace('.csv', '.pdf')
        if os.path.exists(pdf_file_path):
            shutil.move(pdf_file_path, os.path.join(folder, os.path.basename(pdf_file_path)))

        # Borra los archivos csv y pdf originales si existen
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)

        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)

        print(f"Archivos movidos a {folder}")

    def reset_all(self):
        """
        Metodo para reiniciar todas las variables
        
        """
        self.stage_1 = False
        # self.stage_2 = False
        self.stage_3 = False
        # self.stage_4 = False
        self.stage_5 = False
        self.save_button = False

        # self.set_progressbar_2_zero()
        self.disable_all_start_buttons()
        self.disable_save_button()
        self.timer_stage_1.reset()
        self.timer_stage_3.reset()
        self.timer_stage_5.reset()
        self.timer_total.reset()

        self.timer_1.setText("00:00")
        self.timer_2.setText("00:00")
        self.timer_3.setText("00:00")
        self.timer_4.setText("00:00:00")

        self.btn_iniciar_1.setText("Iniciar")
        # self.btn_iniciar_2.setText("Iniciar")
        self.btn_iniciar_3.setText("Iniciar")
        # self.btn_iniciar_4.setText("Iniciar")
        self.btn_iniciar_5.setText("Iniciar")
        self.btn_guardar.setText("Guardar")

        # enable first button
        self.enable_button(self.btn_iniciar_1)
            
    # ============================ Capturar en CSV ============================
    def create_csv(self):
        """
        Metodo para crear un archivo CSV
        Y escribir la cabecera
        """
        cabecera_l1 = ["Archivo de datos del dia ", datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S')]
        cabecera_l2 = ["Etapa", "Fecha", "Hora", "Temperatura_1", "Temperatura_2", "Humedad_1", "RoR", "R", "G", "B"]

        with open(self.file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(cabecera_l1)
            writer.writerow(cabecera_l2)
        print(f"Archivo {self.file_name} creado")

    # Metodo para guardar los datos en un archivo CSV
    def save_data(self, data):
        """
        Metodo para guardar los datos en un archivo CSV
        Se guardan al final de la lista
        
        """
        
        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        print(f"Datos guardados en {self.file_name}")

    def get_comments(self):
        """
        Metodo para obtener los comentarios del text edit
        Se guardan al final de la lista
        """

        comentarios = self.text_cometarios.toPlainText()
        print(comentarios)
        return comentarios
    
    def get_name_and_type(self):
        """
        Metodo para obtener el nombre y tipo de la muestra line text
        Se guardan al final de la lista
        """

        nombre = self.line_cafe.text()
        tipo = self.line_tipo.text()
        return nombre, tipo
    
    def get_kilos_ingresados(self):
        """
        Metodo para obtener los kilos ingresados
        Se guardan al final de la lista
        """
        kilos = self.line_kilos_in.text()
        return kilos
    
    def get_kilos_salida(self):
        """
        Metodo para obtener los kilos de salida
        Se guardan al final de la lista
        """
        kilos = self.line_kilos_out.text()
        return kilos
    
    def get_lote(self):
        """
        Metodo para obtener el lote
        Se guardan al final de la lista
        """
        lote = self.line_lote.text()
        return lote
    
    def get_humedad(self):
        """
        Metodo para obtener la humedad
        Se guardan al final de la lista
        """
        humedad = self.line_hum.text()
        return humedad
    
    def create_graph_for_tostado(self):
        """
        Metodo para crear la grafica de tostado
        Se crea una arcvhivo .png con la grafica de tostado con el mismo nombre que el archivo CSV
        Solo en la etapa 3 (Tostado)
        """
        # Crear la grafica de tostado
        plt = pg.plot(title="Grafica de Tostado")
        plt.setLabel('left', 'Temperatura (°C)')
        plt.setLabel('bottom', 'Tiempo (s)')
        plt.addLegend()

        # Agregar las curvas
        plt.plot(self.t1_x, self.t1_y, pen=pg.mkPen('#FF0000', width=2), name='Temperatura 1')
        plt.plot(self.t2_x, self.t2_y, pen=pg.mkPen('#00FF00', width=2), name='Temperatura 2')
        plt.plot(self.r1_x, self.r1_y, pen=pg.mkPen('#0000FF', width=2), name='RoR')

        # Guardar la grafica como imagen
        image_file = self.file_name.replace('.csv', '.png')
        plt.save(image_file)
        print(f"Grafica guardada como {image_file}")
    

    def create_end_csv(self):
        """
        Metodo para colocar el resumen de los datos en el archivo CSV
        """

        self.tiempo_total = datetime.now() - self.start_time_stage1
        self.tiempo_1 = self.start_time_stage3 - self.start_time_stage1
        # self.tiempo_2 = self.start_time_stage3 - self.start_time_stage2
        self.tiempo_3 = self.start_time_stage5 - self.start_time_stage3
        # self.tiempo_4 = self.start_time_stage5 - self.start_time_stage4
        self.tiempo_5 = datetime.now() - self.start_time_stage5

        # Se crea el resumen de los datos

        name, tipo = self.get_name_and_type()
        comentarios = self.get_comments()
        # resumen.append(f"Nombre: {name}")
        # resumen.append(f"Tipo: {tipo}")
        # resumen.append(f"Comentarios: {comentarios}")
        # resumen.append(f"Kilos ingresados: {self.get_kilos_ingresados()}")
        # resumen.append(f"Kilos de salida: {self.get_kilos_salida()}")
        # resumen.append(f"Lote: {self.get_lote()}")
        # resumen.append(f"Humedad: {self.get_humedad()}")

        l1 = ["Tiempo total: ", self.tiempo_total.total_seconds() // 60, "minutos"]
        l2 = ["Tiempo etapa 1: ", self.tiempo_1.total_seconds() // 60, "minutos"]
        # l3 = ["Tiempo etapa 2: ", self.tiempo_2]
        l4 = ["Tiempo etapa 2: ", self.tiempo_3.total_seconds() // 60, "minutos"]
        # l5 = ["Tiempo etapa 4: ", self.tiempo_4]
        l6 = ["Tiempo etapa 3: ", self.tiempo_5.total_seconds() // 60, "minutos"]

        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(["Resumen de datos"])

            writer.writerow(["Nombre: ", name])
            writer.writerow(["Tipo: ", tipo])
            writer.writerow(["Comentarios: ", comentarios])
            writer.writerow(["Kilos ingresados: ", self.get_kilos_ingresados()])
            writer.writerow(["Kilos de salida: ", self.get_kilos_salida()])
            writer.writerow(["Lote: ", self.get_lote()])
            writer.writerow(["Humedad: ", self.get_humedad()])

            
            writer.writerow(l1)
            writer.writerow(l2)
            # writer.writerow(l3)
            writer.writerow(l4)
            # writer.writerow(l5)
            writer.writerow(l6)

            
        print(f"Resumen guardado en {self.file_name}")

        # time.sleep(3)

        self.reset_all()

        print("Fin de la captura de datos, reiniciando...")
    # ============================ SERIAL ============================
     # Metodo para leer los datos enviados por el microcontrolador

    def read_data(self):
        """
        Metodo para leer los datos enviados por el microcontrolador
        
        """
        if not self.serial.canReadLine(): return
        rx = self.serial.readLine()
        datos = str(rx, 'utf-8').strip()

        # La data debe venir en el siguiente formato:

        # 13,15,8

        print(f"Datos (solo para debug): {datos}")

        # Se parsean los datos
        datos = datos.split(",")

        temperatura_1 = int(datos[0])
        temperatura_2 = int(datos[1])
        humedad_1 = int(datos[2])
        RoR = int(datos[3])
        # color
        # r = int(datos[3])
        # g = int(datos[4])
        # b = int(datos[5])

        self.valor_1.setText(str(temperatura_1))
        self.valor_2.setText(str(temperatura_2))
        self.valor_3.setText(str(humedad_1))
        self.valor_4.setText(str(RoR))
        
        # self.graph_humedad_1(humedad_1)

        # Get dominant color from camera thread
        r, g, b = self.camera_thread.get_dominant_color()
        print(f"Dominant color: {b}, {g}, {r}")
        self.frame_color.setStyleSheet(f"background-color: rgb({b}, {g}, {r});")

        # self.show_color_in_frame(r, g, b)
        # self.color_r.setText(str(r))
        # self.color_g.setText(str(g))
        # self.colo_b.setText(str(b))

        # Se guardan los datos en un archivo CSV

        current_stage = [self.stage_1, self.stage_3, self.stage_5]
        # current_stage_index = current_stage.index(True) + 1 # Doesnt work, (True, true, false) -> 0
        # El current stage index es el indice de la etapa activa voy a sumar todas las etapas activas
        # count de etapas activas
        count = 0
        for i in current_stage:
            if i:
                count += 1
        
        current_stage_index = count
        print(f"Etapa activa: {current_stage_index}")

        name_stage = ["Calentado de Horno", "Tostado", "Enfriado de Cafe"]
        # Solo envia cundo hay una etapa activa
        if current_stage_index != 0:
            # Se guardan los datos en un archivo CSV
            data = [name_stage[current_stage_index - 1], datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), temperatura_1, temperatura_2, humedad_1, RoR, b, g, r]

            self.save_data(data)

        if current_stage_index == 2:
            self.graph_t1_t2_ror(temperatura_1, temperatura_2, RoR + 100) # Se le suma 100 para que la grafica no se vea tan pequeña
            

    # ============================ GRAFICAS ============================
    # Metodo para mostrar los datos en la grafica
    # Error graficando:
    #     Traceback (most recent call last):
    # File "C:\Users\reneg\OneDrive\Documentos\Ingenieria y servicios industriales\sistema tostador\Interfaztostadorrv1\rene\app.py", line 506, in read_data
    #     self.graph_temperatura_1(temperatura_1)
    # File "C:\Users\reneg\OneDrive\Documentos\Ingenieria y servicios industriales\sistema tostador\Interfaztostadorrv1\rene\app.py", line 519, in graph_temperatura_1
    #     self.t1_y = self.y[1:]
    # TypeError: 'builtin_function_or_method' object is not subscriptable
    
    def graph_t1_t2_ror(self, t1, t2, RoR):
        """
        Metodo para mostrar los datos en la misma grafica
        
        """
        self.t1_y = self.t1_y[1:]
        self.t1_y.append(t1)

        self.t2_y = self.t2_y[1:]
        self.t2_y.append(t2)

        self.r1_y = self.r1_y[1:]
        self.r1_y.append(RoR)

        self.plt.clear()
        self.plt.plot(self.t1_x, self.t1_y, pen=pg.mkPen('#FF0000', width=2)) # Rojo
        self.plt.plot(self.t2_x, self.t2_y, pen=pg.mkPen('#00FF00', width=2))
        self.plt.plot(self.r1_x, self.r1_y, pen=pg.mkPen('#0000FF', width=2))

    def graph_temperatura_1(self, temperatura_1):
        """
        Metodo para mostrar los datos en la grafica
        
        """
        temp = int(temperatura_1)
        self.t1_y = self.t1_y[1:]
        self.t1_y.append(temp)

        self.plt.clear()
        self.plt.plot(self.t1_x, self.t1_y, pen=pg.mkPen('#1300FF', width=2))

    def graph_temperatura_2(self, temperatura_2):
        """
        Metodo para mostrar los datos en la grafica
        
        """
        self.t2_y = self.t2_y[1:]
        self.t2_y.append(temperatura_2)

        self.plt2.clear()
        self.plt2.plot(self.t2_x, self.t2_y, pen=pg.mkPen('#1300FF', width=2))

    def graph_humedad_1(self, humedad_1):
        """
        Metodo para mostrar los datos en la grafica
        
        """
        self.h1_y = self.h1_y[1:]
        self.h1_y.append(humedad_1)

        self.plt3.clear()
        self.plt3.plot(self.h1_x, self.h1_y, pen=pg.mkPen('#1300FF', width=2))


    def show_color_in_frame(self, r, g, b):
        """
        Metodo para mostrar el color en el frame
        
        """
        self.frame_rgb.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
        self.frame_rgb.setAutoFillBackground(True)
        
       
    # ============================ INTERFAZ ============================
    # Metodo del boton de menu
    # def mover_menu(self):
    #     if True:
    #         width = self.frame_menu.width()
    #         normal = 0
    #         if width == 0:
    #             extender = 250
    #         else:
    #             extender = normal
    #         self.animacion = QPropertyAnimation(self.frame_menu, b'minimumWidth')
    #         self.animacion.setDuration(300)
    #         self.animacion.setStartValue(width)
    #         self.animacion.setEndValue(extender)
    #         self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
    #         self.animacion.start()

    # Metodo del boton cerrar
    def control_btn_cerrar(self):
        # Detener primero los hilos
        if hasattr(self, 'camera_thread') and self.camera_thread.isRunning():
            self.camera_thread.stop()
        
        # Opcional: Detener otros hilos (ej: TimerThread)
        # if hasattr(self, 'timer_thread') and self.timer_thread.isRunning():
        #     self.timer_thread.stop()
        
        # Cerrar la ventana
        self.close()

    # Metodo del boton de ventana normal
    # def control_btn_normal(self):
    #     self.showNormal()
    #     self.btn_normal.hide()
    #     self.btn_max.show()

    # Metodo del boton de minimizar
    # def control_btn_maximizar(self):
    #     self.showMaximized()
    #     self.btn_max.hide()
    #     self.btn_normal.show()

    # Metodo para redimensionar la ventana
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    def mousePressEvent(self, event):
        self.click_posicion = event.globalPos()

    # Metodo para mover la ventana por la barra de titulo
    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_posicion)
                self.click_posicion = event.globalPos()
                event.accept()
        if event.globalPos().y() <= 5 or event.globalPos().x() <= 5:
            self.showMaximized()
            # self.btn_max.hide()
            # self.btn_normal.show()
        else:
            self.showNormal()
            # self.btn_normal.hide()
            # self.btn_max.show()

    # Metodo para leer los puertos y seleccionar la velocidad de los datos
    def read_ports(self):
        self.baudrates = ['1200', '2400', '4800', '9600', '19200', '34800', '115200']
        portList = []
        ports = QSerialPortInfo().availablePorts()
        for i in ports:
            portList.append(i.portName())

        self.comboBox_puerto.clear()
        self.comboBox_velocidad.clear()
        self.comboBox_puerto.addItems(portList)
        self.comboBox_velocidad.addItems(self.baudrates)
        self.comboBox_velocidad.setCurrentText("115200")      # Se coloca por default una velocidad de  9600 baudios

    # Conexion con las caracteristicas especificadas de velocidad y puerto
    def serial_conect(self):
        self.disable_button(self.btn_conectar)
        self.enable_button(self.btn_desconectar)
        self.serial.waitForReadyRead(100)
        self.port = self.comboBox_puerto.currentText()
        self.baud = self.comboBox_velocidad.currentText()
        self.serial.setBaudRate(int(self.baud))
        self.serial.setPortName(self.port)
        self.serial.open(QIODevice.ReadWrite)

    def serial_desconect(self):
        self.serial.close()
        self.enable_button(self.btn_conectar)
        self.disable_button(self.btn_desconectar)

    # Metodo para enviar datos por comunicacion Serial
    def send_data(self, data):
        data = data + "\n"
        #data = data
        #print(data)
        if self.serial.isOpen():
            self.serial.write(data.encode())
            #print("enviado")

    #### CAMERA ####

    def setup_camera_combobox(self):
        """Rellena el combo box con las cámaras disponibles."""
        self.comboBox_camara.clear()
        max_cameras_to_test = 5  # Número máximo de cámaras a probar
        
        for i in range(max_cameras_to_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.comboBox_camara.addItem(f"{i}", i)
                cap.release()
        if self.comboBox_camara.count() == 0:
            self.comboBox_camara.addItem("No se encontraron cámaras", -1)
    
    def change_camera(self, index):
        """Cambia la cámara cuando se selecciona un ítem del combo box."""
        if index >= 0:
            camera_index = self.comboBox_camara.itemData(index)
            if camera_index != -1:  # -1 sería el caso "No hay cámaras"
                try:
                    self.camera_thread.set_camera(camera_index)
                except Exception as e:
                    print(f"Error al cambiar la cámara: {e}")
    
    def update_camera_view(self, pixmap):
        """Actualiza el QLabel con el frame de la cámara."""
        self.video.setPixmap(pixmap.scaled(
            self.video.width(),
            self.video.height(),
            Qt.KeepAspectRatio
        ))
    
    def closeEvent(self, event):
        if self.camera_thread.isRunning():
            self.camera_thread.stop()
        event.accept()

    # Verifica que el CSV tenga las columnas necesarias
    def validate_columns(self, df, required):
        for col in required:
            if col not in df.columns:
                print(f"❌ ERROR: Falta la columna requerida: '{col}'")
                sys.exit(1)

    def load_and_process_data(self, filepath):
        df = pd.read_csv(filepath, skiprows=1)
        self.validate_columns(df, ['Fecha', 'Hora', 'Etapa', 'Temperatura_1', 'Temperatura_2', 'R', 'G', 'B'])

        df = df[df['Hora'].str.contains(r'\d{2}:\d{2}:\d{2}', na=False)]
        df['Datetime'] = pd.to_datetime(df['Fecha'] + ' ' + df['Hora'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
        df = df.dropna(subset=['Datetime'])
        df = df[df['Etapa'] == 'Tostado'].copy()
        df['Time_seconds'] = (df['Datetime'] - df['Datetime'].iloc[0]).dt.total_seconds()
        df['Time_minutes'] = df['Time_seconds'] / 60
        df = df.rename(columns={'Temperatura_1': 'T1_Grano', 'Temperatura_2': 'T2_Tambor'})
        df['RoR'] = df['T1_Grano'].diff().rolling(window=10, min_periods=1).mean() * 60
        return df

    def identify_phases(self, df):
        key_points = {}
        min_idx = df['T1_Grano'].idxmin()
        t_inicio = df.loc[min_idx, 'Time_minutes']

        # Fase de secado (100°C a 150°C)
        secado_end = df[(df.index > min_idx) & (df['T1_Grano'] >= 150)]
        if not secado_end.empty:
            sec_end_row = secado_end.iloc[0]
            key_points['Secado'] = {
                'Inicio': t_inicio,
                'Fin': sec_end_row['Time_minutes'],
                'Duración': sec_end_row['Time_minutes'] - t_inicio
            }
        else:
            key_points['Secado'] = {'Inicio': t_inicio, 'Fin': t_inicio, 'Duración': 0}

        # Fase de Maillard (150°C a 180°C)
        if not secado_end.empty:
            maillard_end = df[(df.index > secado_end.index[0]) & (df['T1_Grano'] >= 180)]
            if not maillard_end.empty:
                mai_end_row = maillard_end.iloc[0]
                key_points['Maillard'] = {
                    'Inicio': sec_end_row['Time_minutes'],
                    'Fin': mai_end_row['Time_minutes'],
                    'Duración': mai_end_row['Time_minutes'] - sec_end_row['Time_minutes']
                }
            else:
                key_points['Maillard'] = {
                    'Inicio': sec_end_row['Time_minutes'],
                    'Fin': sec_end_row['Time_minutes'],
                    'Duración': 0
                }
        else:
            key_points['Maillard'] = {'Inicio': t_inicio, 'Fin': t_inicio, 'Duración': 0}

        return key_points

    def identify_key_events(self, df):
        key_points = {}
        key_points['Tiempo Total'] = df['Time_minutes'].iloc[-1]

        # Primer crack (T1 entre 190 y 205 y RoR más alto)
        crack_df = df[(df['T1_Grano'] >= 190) & (df['T1_Grano'] <= 205)]
        if not crack_df.empty:
            crack_idx = crack_df['RoR'].idxmax()
            key_points['Primer Crack'] = {
                'Tiempo': df.loc[crack_idx, 'Time_minutes'],
                'T1': df.loc[crack_idx, 'T1_Grano'],
                'T2': df.loc[crack_idx, 'T2_Tambor'],
                'RoR': df.loc[crack_idx, 'RoR'],
                'es_RoR': False
            }

        # Pico RoR
        ror_peak_idx = df['RoR'].idxmax()
        key_points['Pico RoR'] = {
            'Tiempo': df.loc[ror_peak_idx, 'Time_minutes'],
            'T1': df.loc[ror_peak_idx, 'RoR'],
            'RoR': df.loc[ror_peak_idx, 'RoR'],
            'es_RoR': True
        }

        # Temperaturas específicas alcanzadas
        min_idx = df['T1_Grano'].idxmin()
        for temp in [150, 170, 180, 200]:
            subset = df[(df.index > min_idx) & (df['T1_Grano'] > temp)]
            if not subset.empty:
                idx = subset.index[0]
                key_points[f'T1 alcanza {temp}°C'] = {
                    'Tiempo': df.loc[idx, 'Time_minutes'],
                    'T1': df.loc[idx, 'T1_Grano'],
                    'es_RoR': False
                }
            else:
                key_points[f'T1 alcanza {temp}°C'] = {'Tiempo': 0, 'T1': 0, 'es_RoR': False}

        key_points['Correlación T1-T2'] = df['T1_Grano'].corr(df['T2_Tambor'])

        return key_points

    def analyze_rgb(self, df):
        df['Luminosidad'] = df[['R', 'G', 'B']].mean(axis=1)
        df['Cambio_RGB'] = df['Luminosidad'].diff().abs()
        max_idx = df['Cambio_RGB'].idxmax()
        return {
            'Máximo Cambio RGB': {
                'Tiempo': df.loc[max_idx, 'Time_minutes'],
                'T1': df.loc[max_idx, 'T1_Grano'],
                'RGB': (df.loc[max_idx, 'R'], df.loc[max_idx, 'G'], df.loc[max_idx, 'B']),
                'Luminosidad': df.loc[max_idx, 'Luminosidad']
            }
        }

    def create_pdf_report(self, df, eventos, fases, rgb, filename="reporte_tostado_final.pdf"):
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = [12, 8]
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3

        with PdfPages(filename) as pdf:
            fig, ax1 = plt.subplots()
            ax1.plot(df['Time_minutes'], df['T1_Grano'], 'r-', label='T1 (Grano)')
            ax1.plot(df['Time_minutes'], df['T2_Tambor'], 'm-', label='T2 (Tambor)')
            ax2 = ax1.twinx()
            ax2.plot(df['Time_minutes'], df['RoR'], 'b-', label='RoR', alpha=0.7)

            ax1.set_xlabel("Tiempo (min)")
            ax1.set_ylabel("Temperatura (°C)", color='red')
            ax2.set_ylabel("RoR (°C/min)", color='blue')
            ax1.set_title("Perfil de Tostado con Eventos Clave")

            for label, data in eventos.items():
                if isinstance(data, dict) and 'Tiempo' in data:
                    if data.get('es_RoR', False):
                        ax2.scatter(data['Tiempo'], data['T1'], label=label, s=100)
                        ax2.text(data['Tiempo'], data['T1'] + 1, label, fontsize=9, ha='center')
                    else:
                        ax1.scatter(data['Tiempo'], data['T1'], label=label, s=100)
                        ax1.text(data['Tiempo'], data['T1'] + 5, label, fontsize=9, ha='center')

            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            # Texto del reporte
            lines = []
            lines.append("=== REPORTE DE TOSTADO ===")
            lines.append(f"Tiempo total: {eventos['Tiempo Total']:.2f} minutos\n")

            for fase, val in fases.items():
                lines.append(f"--- Fase de {fase} ---")
                for k, v in val.items():
                    lines.append(f"{k}: {v:.2f} min")
                lines.append("")

            for k, v in eventos.items():
                if isinstance(v, dict):
                    lines.append(f"--- {k} ---")
                    for subk, subv in v.items():
                        if subk != 'es_RoR':
                            lines.append(f"{subk}: {subv:.2f}")
                    lines.append("")

            lines.append("--- Correlación T1-T2 ---")
            lines.append(f"{eventos['Correlación T1-T2']:.3f}\n")

            rgb_ev = rgb['Máximo Cambio RGB']
            lines.append("--- Análisis de Color ---")
            lines.append(f"Tiempo: {rgb_ev['Tiempo']:.2f} min")
            lines.append(f"T1: {rgb_ev['T1']:.2f} °C")
            lines.append(f"Luminosidad: {rgb_ev['Luminosidad']:.2f}")
            lines.append(f"RGB: {rgb_ev['RGB']}")

            for i in range(0, len(lines), 30):
                fig, ax = plt.subplots(figsize=(11, 8))
                ax.axis('off')
                ax.text(0.05, 0.95, "\n".join(lines[i:i+30]), va='top', ha='left', fontsize=12, family='monospace')
                pdf.savefig()
                plt.close()

            print(f"✅ PDF generado como: {filename}")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyApp()
    window.show()
    app.exec_()