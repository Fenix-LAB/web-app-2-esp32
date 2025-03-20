from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo   # Modulo Serial de PyQt5
from PyQt5.QtCore import *                                    # Modulo PyQt5 para intarfaces graficas
from gui_design import *
from PyQt5.QtGui import *
import time
from datetime import datetime
import csv
import pyqtgraph as pg
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal, QDateTime

class TimerThread(QThread):
    update_time = pyqtSignal(str)  # Señal para actualizar el tiempo en el QLabel

    def __init__(self, label, format="mm:ss"):
        super().__init__()
        self.label = label  # QLabel que mostrará el tiempo
        self.format = format  # Formato de tiempo: "mm:ss" o "hh:mm:ss"
        self.running = False  # Estado del cronómetro
        self.start_time = None  # Tiempo de inicio

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
        self.t1_x = list(np.linspace(0, 50, 50))
        self.t1_y = list(np.linspace(0, 0, 50))

        self.t2_x = list(np.linspace(0, 50, 50))
        self.t2_y = list(np.linspace(0, 0, 50))

        self.h1_x = list(np.linspace(0, 50, 50))
        self.h1_y = list(np.linspace(0, 0, 50))

        # Creacion de la grafica 1
        pg.setConfigOption('background', '#ebfeff')
        pg.setConfigOption('foreground', '#000000')
        self.plt = pg.PlotWidget()
        self.graph_1.addWidget(self.plt)

        pg.setConfigOption('background', '#ebfeff')
        pg.setConfigOption('foreground', '#000000')
        self.plt2 = pg.PlotWidget()
        self.graph_2.addWidget(self.plt2)

        pg.setConfigOption('background', '#ebfeff')
        pg.setConfigOption('foreground', '#000000')
        self.plt3 = pg.PlotWidget()
        self.graph_3.addWidget(self.plt3)

        # Asociacion de metodos
        self.serial.readyRead.connect(self.read_data)
        self.read_ports()

        # self.set_progressbar_2_zero()
        self.disable_all_start_buttons()
        self.disable_save_button()

        # enable first button
        self.enable_button(self.btn_iniciar_1)
        self.disable_button(self.btn_desconectar)

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
        self.change_button_text(self.btn_guardar, "Guardado")


        self.disable_save_button()

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

        # enable first button
        self.enable_button(self.btn_iniciar_1)
            
    # ============================ Capturar en CSV ============================
    def create_csv(self):
        """
        Metodo para crear un archivo CSV
        Y escribir la cabecera
        """
        cabecera_l1 = ["Archivo de datos del dia ", datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S')]
        cabecera_l2 = ["Etapa", "Fecha", "Hora", "Temperatura_1", "Temperatura_2", "Humedad_1"]

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

        l1 = ["Tiempo total: ", self.tiempo_total]
        l2 = ["Tiempo etapa 1: ", self.tiempo_1]
        # l3 = ["Tiempo etapa 2: ", self.tiempo_2]
        l4 = ["Tiempo etapa 2: ", self.tiempo_3]
        # l5 = ["Tiempo etapa 4: ", self.tiempo_4]
        l6 = ["Tiempo etapa 3: ", self.tiempo_5]

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

        # Se guardan los datos en un archivo CSV

        current_stage = [self.stage_1, self.stage_2, self.stage_3, self.stage_4, self.stage_5]
        # current_stage_index = current_stage.index(True) + 1 # Doesnt work, (True, true, false) -> 0
        # El current stage index es el indice de la etapa activa voy a sumar todas las etapas activas
        # count de etapas activas
        count = 0
        for i in current_stage:
            if i:
                count += 1
        
        current_stage_index = count
        print(f"Etapa activa: {current_stage_index}")

        name_stage = ["Calentado de Horno", "Ingreso de Cafe", "Tostado", "Salida de Cafe", "Enfriado de Cafe"]
        # Solo envia cundo hay una etapa activa
        if current_stage_index != 0:
            # Se guardan los datos en un archivo CSV
            data = [name_stage[current_stage_index - 1], datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), temperatura_1, temperatura_2, humedad_1]

            self.save_data(data)
            # Se muestran los datos en la las graficas
            self.graph_temperatura_1(temperatura_1)
            self.graph_temperatura_2(temperatura_2)
            self.graph_humedad_1(humedad_1)



    # ============================ GRAFICAS ============================
    # Metodo para mostrar los datos en la grafica
    # Error graficando:
    #     Traceback (most recent call last):
    # File "C:\Users\reneg\OneDrive\Documentos\Ingenieria y servicios industriales\sistema tostador\Interfaztostadorrv1\rene\app.py", line 506, in read_data
    #     self.graph_temperatura_1(temperatura_1)
    # File "C:\Users\reneg\OneDrive\Documentos\Ingenieria y servicios industriales\sistema tostador\Interfaztostadorrv1\rene\app.py", line 519, in graph_temperatura_1
    #     self.t1_y = self.y[1:]
    # TypeError: 'builtin_function_or_method' object is not subscriptable
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
        self.close()
        # cap.release()
        self.label.clear()

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
            self.btn_max.hide()
            self.btn_normal.show()
        else:
            self.showNormal()
            self.btn_normal.hide()
            self.btn_max.show()

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


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyApp()
    window.show()
    app.exec_()