from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from Backend.settings import MEDIA_ROOT, MEDIA_URL
from MainApp.models import Audio

import torchaudio
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
    audio_file = f'audio_{identificador_unico}.wav'
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
        try:
         text = extraer_texto(image_data)
         if text != None:
         # Generar archivo de audio y obtener la URL
          audio_url = generar_audio(text)
          
          # Devolver la URL del archivo de audio en formato JSON
          return JsonResponse({'audio_url': audio_url})

        except:
         print('No hay texto en la imagen')
         return JsonResponse({'status': 'error', 'message': 'No hay texto en la imagen'})

        
        

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


@csrf_exempt
def cambiarTono(request):  
  
  if request.method == 'POST':
    
     data_audio = request.POST.get('data_audio')
     tono = request.POST.get('tono')
     
     # Cargar el archivo de audio
     audio, sample_rate = torchaudio.load(os.path.join(MEDIA_ROOT, 'audio', data_audio))
     if tono == 'agudo':
         # Definir el factor de cambio de tono
         factor = -0.1 # reducir el tono a la mitad
         # Cambiar el tono del audio
         
         audio_changed_tone = torchaudio.transforms.Resample(sample_rate, int(sample_rate*(1+factor)))(audio)
     elif tono == 'grave':
         # Definir el factor de cambio de tono
         factor = 0.1 # reducir el tono a la mitad
         # Cambiar el tono del audio
         
         audio_changed_tone = torchaudio.transforms.Resample(sample_rate, int(sample_rate*(1+factor)))(audio)    
     ruta = os.path.join(MEDIA_ROOT, 'audio', data_audio)
     # Guardar el archivo de audio modificado
     torchaudio.save(ruta, audio_changed_tone, sample_rate)
     return JsonResponse({'status': 'success', 'message': 'Tono Convertido'})
   
