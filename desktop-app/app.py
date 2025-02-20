from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo   # Modulo Serial de PyQt5
from PyQt5.QtCore import *                                    # Modulo PyQt5 para intarfaces graficas
from gui_design import *
from PyQt5.QtGui import *
import time

#Clase de la ventana heredada de la interfaz "gui_design.py"
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    # Se define le contructor con todos los atributos necesarios y asociacion de metodos
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Usamos la funcion QPoint() para guardar la posicion del mouse
        self.click_position = QPoint()
        self.btn_menu.clicked.connect(self.mover_menu)

        # Se configura la ventana asociando los eventos con metodos
        self.btn_normal.hide()
        self.btn_min.clicked.connect(lambda: self.showMinimized())
        self.btn_cerrar.clicked.connect(self.control_btn_cerrar)
        self.btn_normal.clicked.connect(self.control_btn_normal)
        self.btn_max.clicked.connect(self.control_btn_maximizar)
        # self.btn_45_grd.clicked.connect(self.set_45_degrees)
        # self.btn_55_grd.clicked.connect(self.set_55_degrees)
        # self.btn_boca_cerrada.clicked.connect(self.set_0_degrees)
        # self.btn_guardar.clicked.connect(self.guardar_datos)


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
        self.btn_desconectar.clicked.connect(lambda: self.serial.close())

        # Asociacion de metodos
        self.serial.readyRead.connect(self.read_data)
        self.read_ports()

        self.set_progressbar_2_zero()
        self.disable_all_start_buttons()
        self.disable_save_button()

    def set_progressbar_2_zero(self):
        """
        Metodo para poner en 0 todas las barras de progreso
        
        """
        self.prog_1.setValue(0)
        self.prog_2.setValue(0)
        self.prog_3.setValue(0)
        self.prog_4.setValue(0)
        self.prog_5.setValue(0)

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
        self.btn_iniciar_2.setEnabled(False)
        self.btn_iniciar_3.setEnabled(False)
        self.btn_iniciar_4.setEnabled(False)
        self.btn_iniciar_5.setEnabled(False)

        # Now change style to grayed out
        self.btn_iniciar_1.setStyleSheet(style_grayed_out)
        self.btn_iniciar_2.setStyleSheet(style_grayed_out)
        self.btn_iniciar_3.setStyleSheet(style_grayed_out)
        self.btn_iniciar_4.setStyleSheet(style_grayed_out)
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

    def read_data(self):
        """
        Metodo para leer los datos enviados por el microcontrolador
        
        """
        if not self.serial.canReadLine(): return
        rx = self.serial.readLine()
        datos = str(rx, 'utf-8').strip()

        # La data debe venir en el siguiente formato:
        # psa:1,psb:0,psc:1,msa:0,msb:1,msc:0

        print(f"Datos (solo para debug): {datos}")

        # Se separan los datos
        for data in datos.split(","):
            data = data.split(":")
            sensor = data[0]
            status = data[1]
            self.change_diente_status(sensor, bool(int(status)))

       

    # Metodo del boton de menu
    def mover_menu(self):
        if True:
            width = self.frame_menu.width()
            normal = 0
            if width == 0:
                extender = 250
            else:
                extender = normal
            self.animacion = QPropertyAnimation(self.frame_menu, b'minimumWidth')
            self.animacion.setDuration(300)
            self.animacion.setStartValue(width)
            self.animacion.setEndValue(extender)
            self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animacion.start()

    # Metodo del boton cerrar
    def control_btn_cerrar(self):
        self.close()
        # cap.release()
        self.label.clear()

    # Metodo del boton de ventana normal
    def control_btn_normal(self):
        self.showNormal()
        self.btn_normal.hide()
        self.btn_max.show()

    # Metodo del boton de minimizar
    def control_btn_maximizar(self):
        self.showMaximized()
        self.btn_max.hide()
        self.btn_normal.show()

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
        self.serial.waitForReadyRead(100)
        self.port = self.comboBox_puerto.currentText()
        self.baud = self.comboBox_velocidad.currentText()
        self.serial.setBaudRate(int(self.baud))
        self.serial.setPortName(self.port)
        self.serial.open(QIODevice.ReadWrite)

    
        

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