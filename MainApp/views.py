from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from Backend.settings import MEDIA_ROOT, MEDIA_URL

import cv2
from gtts import gTTS
import pytesseract
import os
import numpy as np
import uuid

# Define una función para extraer texto de una imagen


def extraer_texto(image_data):

    # Convierte los bytes de la imagen a un array numpy
    nparr = np.frombuffer(image_data.read(), np.uint8)
    # Decodifica la imagen y carga en OpenCV
    imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Extrae texto de la imagen utilizando tesseract OCR
    text = pytesseract.image_to_string(imagen)

    return text

# Define una función para generar audio a partir de texto


def generar_audio(text):

    # Generar un identificador único
    identificador_unico = str(uuid.uuid4())

    # Genera un archivo de audio utilizando gTTS
    tts = gTTS(text=text, lang='es')
    audio_file = f'audio_{identificador_unico}.mp3'
    audio_path = os.path.join(MEDIA_ROOT, 'audio', audio_file)
    tts.save(audio_path)

    # Devuelve la URL del archivo de audio
    audio_url = os.path.join(MEDIA_URL, 'audio', audio_file).replace("\\", "/")

    return audio_url

# Define la vista que procesa la imagen y devuelve la URL del audio generado


@csrf_exempt
def procesar_imagen(request):

    if request.method == 'POST':
        # Obtener la imagen del cuerpo de la solicitud
        image_data = request.FILES.get('image_data')

        # Extraer texto de la imagen
        text = extraer_texto(image_data)

        # Generar archivo de audio y obtener la URL
        audio_url = generar_audio(text)

        # Devolver la URL del archivo de audio en formato JSON
        return JsonResponse({'audio_url': audio_url})
