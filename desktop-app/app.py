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
        self.btn_45_grd.clicked.connect(self.set_45_degrees)
        self.btn_55_grd.clicked.connect(self.set_55_degrees)
        self.btn_boca_cerrada.clicked.connect(self.set_0_degrees)
        self.btn_guardar.clicked.connect(self.guardar_datos)

        self.status_dientes = {
            "ps1": False,
            "ms1": False,
            "ps2": False,
            "ms2": False,
            "ps3": False,
            "ms3": False
        }

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

    def set_55_degrees(self):
        """
        Metodo para enviar la imagen de la boca a 55 grados
        """
        self.img_boca.setPixmap(QPixmap("images/boca_55.png"))
        self.send_data("55")
        # self.simulate_cambio_dientes()

    def set_0_degrees(self):
        """
        Metodo para enviar la imagen de la boca a 0 grados
        """
        self.img_boca.setPixmap(QPixmap("images/bocs_cerrada.png"))
        self.send_data("0")

    def set_45_degrees(self):
        """
        Metodo para enviar la imagen de la boca a 45 grados
        """
        self.img_boca.setPixmap(QPixmap("images/bocs_45.png"))
        self.send_data("45")


    def change_diente_status(self, sensor: str , status: bool) -> dict:
        """
        El color del diente cambia dependiendo del estado del sensor
        
        Args:
            sensor (str): Nombre del sensor (ps1, ms1, ps2, ms2, ps3, ms3)
            status (bool): Estado del sensor (True: para color verde, False: color blanco)
        """
        # Se cambia el color del diente
        print(f"change {sensor} a {status}")
        if sensor == "ps1":
            if status:
                self.pre_sensor_1.setPixmap(QPixmap("images/premolar_verde.png"))
            else:
                self.pre_sensor_1.setPixmap(QPixmap("images/premolar_blanco.png"))

        if sensor == "ms1":
            if status:
                self.mo_sensor_1.setPixmap(QPixmap("images/molar_verde.png"))
            else:
                self.mo_sensor_1.setPixmap(QPixmap("images/molar_blanco.png"))

        if sensor == "ps2":
            if status:
                self.pre_sensor_2.setPixmap(QPixmap("images/premolar_verde.png"))
            else:
                self.pre_sensor_2.setPixmap(QPixmap("images/premolar_blanco.png"))

        if sensor == "ms2":
            if status:
                self.mo_sensor_2.setPixmap(QPixmap("images/molar_verde.png"))
            else:
                self.mo_sensor_2.setPixmap(QPixmap("images/molar_blanco.png"))

        if sensor == "ps3":
            if status:
                self.pre_sensor_3.setPixmap(QPixmap("images/premolar_verde.png"))
            else:
                self.pre_sensor_3.setPixmap(QPixmap("images/premolar_blanco.png"))

        if sensor == "ms3":
            if status:
                self.mo_sensor_3.setPixmap(QPixmap("images/molar_verde.png"))
            else:
                self.mo_sensor_3.setPixmap(QPixmap("images/molar_blanco.png"))

        # Return actual status de los sensores
        self.status_dientes[sensor] = status
        print('done')
        # print(self.status_dientes)
        return self.status_dientes
        

    def simulate_cambio_dientes(self):  
        """
        Metodo para simular el cambio de estado de los sensores
        """
        self.change_diente_status("ps1", not self.status_dientes["ps1"])
        self.change_diente_status("ms1", not self.status_dientes["ms1"])
        self.change_diente_status("ps2", not self.status_dientes["ps2"])
        self.change_diente_status("ms2", not self.status_dientes["ms2"])
        self.change_diente_status("ps3", not self.status_dientes["ps3"])
        self.change_diente_status("ms3", not self.status_dientes["ms3"])

    def guardar_datos(self):
        """
        Metodo para guardar los datos de los sensores en la tabla y generar un excel
        """
        # Se obtiene la fecha y hora actual
        fecha = time.strftime("%d-%m-%Y")
        hora = time.strftime("%H-%M-%S")
        nombre = self.line_nombre.text()
        matricula = self.line_matricula.text()
        # Se crea el nombre del archivo
        # nombre_archivo = f"datos_sensores_{fecha}_{hora}.csv"

        # Se crea el archivo

        # Guardar en la tabla
        # self.table_datos.setRowCount(0)
        self.table_datos.insertRow(0)
        self.table_datos.setItem(0, 0, QtWidgets.QTableWidgetItem(nombre))
        self.table_datos.setItem(0, 1, QtWidgets.QTableWidgetItem(matricula))
        self.table_datos.setItem(0, 2, QtWidgets.QTableWidgetItem(str(self.status_dientes["ps1"])))
        self.table_datos.setItem(0, 3, QtWidgets.QTableWidgetItem(str(self.status_dientes["ms1"])))
        self.table_datos.setItem(0, 4, QtWidgets.QTableWidgetItem(str(self.status_dientes["ps2"])))
        self.table_datos.setItem(0, 5, QtWidgets.QTableWidgetItem(str(self.status_dientes["ms2"])))
        self.table_datos.setItem(0, 6, QtWidgets.QTableWidgetItem(str(self.status_dientes["ps3"])))
        self.table_datos.setItem(0, 7, QtWidgets.QTableWidgetItem(str(self.status_dientes["ms3"])))
        self.table_datos.setItem(0, 8, QtWidgets.QTableWidgetItem(fecha))
        self.table_datos.setItem(0, 9, QtWidgets.QTableWidgetItem(hora))

    def read_data(self):
        """
        Metodo para leer los datos enviados por el microcontrolador
        El microcontrolador envia los datos de los sensores en el siguiente formato:
        psa:1,psb:1,psc:1,msa:1,msb:1,msc:1

        Donde:
        psa1: Estado del sensor pre_sensor_1 1: activo, 0: inactivo
        psb1: Estado del sensor pre_sensor_2 1: activo, 0: inactivo
        psc1: Estado del sensor pre_sensor_3 1: activo, 0: inactivo
        msa1: Estado del sensor mo_sensor_1 1: activo, 0: inactivo
        msb1: Estado del sensor mo_sensor_2 1: activo, 0: inactivo
        msc1: Estado del sensor mo_sensor_3 1: activo, 0: inactivo

        Favor de costruir el microcontrolador con este formato de envio de datos
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