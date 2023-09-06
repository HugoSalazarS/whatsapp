import pandas as pd
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from pyautogui import click, hotkey, locateOnScreen, moveTo, press, size, typewrite
import time
import tempfile
import os
from platform import system
import webbrowser as web
from urllib.parse import quote
from typing import List
from pyautogui import click, hotkey, locateOnScreen, moveTo, press, size, typewrite

app = Flask(__name__)

CORS(app)

# Directorio temporal para guardar los archivos
TEMP_DIR = tempfile.gettempdir()
cached_data = None  # Variable global para almacenar los datos en caché
columnas_principales = []  # Variable global para almacenar los nombres de las columnas principales
columna_numero = None  # Variable global para almacenar la columna que contiene los números de teléfono

WIDTH, HEIGHT = size()

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para cargar el archivo
@app.route('/cargar-archivo', methods=['POST'])
def cargar_archivo():
    file = request.files['file']

    # Verificar si el archivo es un archivo CSV válido
    if not file.filename.endswith('.csv'):
        print('Error: El archivo no es un archivo CSV válido')
        return jsonify({'error': 'Formato de archivo no válido'})

    data = get_data(file)
    if data is None:
        return jsonify({'error': 'Formato de archivo no válido'})

    global cached_data
    global columnas_principales
    cached_data = data
    columnas_principales = data.columns.tolist()

    return jsonify({'success': True, 'message': 'Archivo cargado correctamente'})


# Ruta para enviar los mensajes
@app.route('/enviar-mensajes', methods=['POST'])
def enviar_mensajes():
    if cached_data is None:
        return jsonify({'error': 'No se ha cargado ningún archivo'})

    if columna_numero is None:
        return jsonify({'error': 'No se ha seleccionado la columna de número'})

    numeros = cached_data[columna_numero]
    mensaje_personalizado = request.form['mensaje']

    # Iterar sobre los datos de cada columna
    for index, row in cached_data.iterrows():
        mensaje = mensaje_personalizado  # Reiniciar el mensaje personalizado para cada fila

        # Reemplazar los marcadores de columna en el mensaje personalizado
        for col in columnas_principales:
            marcador = f"[{col}]"
            if marcador in mensaje:
                valor_celda = row[col]
                mensaje = mensaje.replace(marcador, str(valor_celda))

        numero = str(row[columna_numero])  # Obtener el número de teléfono de la columna seleccionada
        sendmsj(numero, mensaje, 15, True, 3)  # Enviar mensaje de WhatsApp

    return jsonify({'success': True, 'message': 'Mensajes enviados correctamente'})


# Ruta para obtener los nombres de las columnas principales
@app.route('/nombres-columnas', methods=['GET'])
def nombres_columnas():
    if cached_data is None:
        return jsonify({'error': 'No se ha cargado ningún archivo'})

    return jsonify({'columnas_principales': columnas_principales})


# Ruta para seleccionar la columna de número
@app.route('/numero-columna', methods=['POST'])
def numero_columna():
    global columna_numero
    columna_numero = request.form['columna']
    return jsonify({'success': True, 'message': 'Columna de número seleccionada correctamente'})


# Función para leer los datos del archivo y guardarlos en caché
def get_data(file):
    # Verificar si el archivo es un archivo CSV válido
    if not file.filename.endswith('.csv'):
        print('Error: El archivo no es un archivo CSV válido')
        return None

    # Guardar archivo en el directorio temporal
    temp_file_path = os.path.join(TEMP_DIR, file.filename)
    file.save(temp_file_path)

    # Cargar archivo CSV en memoria
    data = pd.read_csv(temp_file_path, encoding='utf-8', sep='[;,]', dtype=str)
    print(data)

    return data

# Función para mandar mensaje

def sendmsj(
        phone_no: str,
        message: str,
        wait_time: int = 20,
        tab_close: bool = False,
        close_time: int = 3,
) -> None:
    """Send WhatsApp Message Instantly"""

    web.open(f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}")
    time.sleep(4)
    click(WIDTH / 2, HEIGHT / 2 + 15)
    time.sleep(wait_time - 4)
    press("enter")
    if tab_close:
        time.sleep(2)
        _system = system().lower()
        if _system in ("windows", "linux"):
            hotkey("ctrl", "w")
        elif _system == "darwin":
            hotkey("command", "w")
        else:
            raise Warning(f"{_system} not supported!")
        press("enter")

'''def sendmsj(Number, mensaje):
    numero = "+" + Number  # Agregar el código de país al número
    pw.sendwhatmsg_instantly(numero, mensaje, 15)
    pa.click(WIDTH / 2, HEIGHT / 2 + 15)
    time.sleep(4)
    pa.press('enter')
    time.sleep(1)
    # Cerrar la ventana según el sistema operativo
    system = platform.system()
    if system == 'Windows':
        pa.hotkey('ctrl', 'w')
    elif system == 'Darwin':  # macOS
        pa.hotkey('command', 'w')
    elif system == 'Linux':
        pa.hotkey('ctrl', 'w')
    else:
        # Sistema operativo no compatible, realizar alguna acción por defecto o mostrar un mensaje de error
        print('Sistema operativo no compatible')
'''

if __name__ == '__main__':
    app.run(threaded=True)