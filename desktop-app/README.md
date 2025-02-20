# Aplicacion de escritorio para herramienta de Dentistas
## Descripción
Aplicación de escritorio para la...

## Requisitos
- Python 3.10
- Qt Designer
- Verifca que python este bien instalado, yo uso el que se descarga en Microsoft Store y me funciona bien.
```bash
python --version
```

## Instalación
1. Clonar el repositorio (o descargarlo)
2. Crear un entorno virtual:
```bash
python -m venv venv
```
3. Activar el entorno virtual:
```bash
venv/Scripts/activate
```
4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```
5. Ejecutar la aplicación:
```bash
python app.py
```

## Crear .py a partir de .ui
1. Crear el archivo .py a partir del .ui:
```bash
pyuic6 -x archivo.ui -o archivo.py
# Para este caso:
pyuic5 -x GUI-2.ui -o gui_design.py
``` 

## Abrir Qt Designer
Abre la carpeta de QT -> bin -> designer.exe

## Generar ejecutable con PyInstaller
1. Instalar PyInstaller:
```bash
pip install pyinstaller
```
2. Crear el ejecutable, en la carpeta del proyecto (iconos, imagesn etc. deben estar en la misma carpeta):
```bash
pyinstaller --onefile --windowed app.py
```
3. Ejecutar el ejecutable:
```bash
dist/app.exe
```