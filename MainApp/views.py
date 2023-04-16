from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from Backend.settings import MEDIA_ROOT, MEDIA_URL

from MainApp.models import Audio

# import cv2
from gtts import gTTS
import pytesseract
import os
# import numpy as np
import uuid
import base64
from PIL import Image
import io


# Define una función para extraer texto de una imagen
def extraer_texto(image_data):

    # Decodificar la imagen desde base64
    imagen = base64.b64decode(image_data)

    # Convierte los bytes de la imagen a un objeto Image de Pillow
    imagen = Image.open(io.BytesIO(imagen))

    # Redimensionar la imagen si es necesario
    width, height = imagen.size
    if width > 1000:
        imagen = imagen.resize((int(width / 2), int(height / 2)))

    # Extrae texto de la imagen utilizando tesseract OCR
    text = pytesseract.image_to_string(imagen, lang='spa_old')

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
        image_data = request.POST.get('image_data')

        # Extraer texto de la imagen
        text = extraer_texto(image_data)

        # Generar archivo de audio y obtener la URL
        audio_url = generar_audio(text)

        # Devolver la URL del archivo de audio en formato JSON
        return JsonResponse({
            'audio_url': audio_url,
            'texto': text,
        })


@csrf_exempt
def guardar_audio(request):

    if request.method == 'POST':

        audio = request.POST.get('audio')
        name = request.POST.get('name')
        id_user = request.POST.get('id_user')

        # Ruta del archivo
        ruta_archivo = os.path.join(MEDIA_ROOT, 'audio', audio)

        # Verificar si el archivo existe
        if os.path.isfile(ruta_archivo):

            # Crear un objeto Audio con los datos del formulario
            nuevo_audio = Audio(name=name, user_id=id_user, audio=audio)
            nuevo_audio.save()

            # Devolver respuesta exitosa
            return JsonResponse({'status': 'success', 'message': 'Audio guardado con exito'})

        else:
            # Devolver respuesta de error
            return JsonResponse({'status': 'error', 'message': 'El audio no existe'})

    # Devolver respuesta de error en caso de que no sea una petición POST
    return JsonResponse({'status': 'error', 'message': 'Petición inválida'})
