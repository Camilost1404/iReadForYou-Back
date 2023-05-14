from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from Backend.settings import MEDIA_ROOT, MEDIA_URL
from MainApp.models import Audio, User

from textblob import TextBlob
from langdetect import detect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

import torchaudio
# from gtts import gTTS
import speech_recognition as sr
import pyttsx3
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
    tts = pyttsx3.init()
    audio_file = f'audio_{identificador_unico}.wav'
    audio_path = os.path.join(MEDIA_ROOT, 'audio', audio_file)
    tts.save_to_file(text, audio_path)
    tts.runAndWait()

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
        try:
            text = extraer_texto(image_data)
            if text != None:
                text = text.replace('\n', ' ')

                # Detectar el idioma en el que esta el texto
                deteccion = detect(text)
                if deteccion == 'en':
                    blob = TextBlob(text)
                    # Traduce desde el ingles hacia el español
                    blob = blob.translate(from_lang='en', to='es')
                    # Convierte en string la traduccion que esta en la variable blob y se la da a text
                    text = str(blob)
                    # Generar audio
                    audio_url = generar_audio(text)

                    # Devolver la URL del archivo de audio en formato JSON
                    return JsonResponse({
                        'audio_url': audio_url,
                        'texto': text,
                    })

                elif deteccion == 'es':

                    audio_url = generar_audio(text)

                    # Devolver la URL del archivo de audio en formato JSON
                    return JsonResponse({
                        'audio_url': audio_url,
                        'texto': text,
                    })

                else:

                    return JsonResponse({'status': 'error', 'message': 'El lenguaje en el que se encuentra el texto no es admitido'})

        except:

            return JsonResponse({'status': 'error', 'message': 'No hay texto en la imagen'})


@csrf_exempt
def guardar_audio(request):

    if request.method == 'POST':

        audio = request.POST.get('audio')
        name = request.POST.get('name')
        id_user = request.POST.get('id_user')

        if '-modificado' in audio:

            audio.split('-modificado')[0]
            audio = f'{audio}.wav'

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
        audio, sample_rate = torchaudio.load(
            os.path.join(MEDIA_ROOT, 'audio', data_audio))

        if tono == 'agudo':
            # Definir el factor de cambio de tono
            factor = -0.1  # reducir el tono a la mitad

            # Cambiar el tono del audio
            audio_changed_tone = torchaudio.transforms.Resample(
                sample_rate, int(sample_rate*(1+factor)))(audio)
        elif tono == 'grave':
            # Definir el factor de cambio de tono
            factor = 0.1  # reducir el tono a la mitad
            # Cambiar el tono del audio

            audio_changed_tone = torchaudio.transforms.Resample(
                sample_rate, int(sample_rate*(1+factor)))(audio)

        if 'modificado' not in data_audio:
            data_audio = data_audio.split('.')[0]
            data_audio += '-modificado.wav'

        ruta = os.path.join(MEDIA_ROOT, 'audio', data_audio)

        # Devuelve la URL del archivo de audio
        audio_url = os.path.join(
            MEDIA_URL, 'audio', data_audio).replace("\\", "/")

        # Guardar el archivo de audio modificado
        torchaudio.save(ruta, audio_changed_tone, sample_rate)

        return JsonResponse({'audio_url': audio_url, })


@csrf_exempt
def mostrar_audios(request):
    id_user = request.GET.get('id_user')
    audios = list(Audio.objects.filter(user_id=id_user).values())
    return JsonResponse(audios, safe=False)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserInfo(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = User.objects.filter(email=request.user)

        # convert QuerySet to list of dictionaries
        users_list = list(user.values())

        return JsonResponse({
            'user': users_list
        }, status=status.HTTP_200_OK)


class UserRegister(APIView):

    def post(self, request):
        name = request.data['name']
        password = request.data['password']
        email = request.data['email']
        last_name = request.data['last_name']
        try:
            user = User.objects.create_user(
                name=name, password=password, email=email, last_name=last_name)
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data)
        except:
            return Response({'error': 'Error al crear usuario'})


@csrf_exempt
def audio_especifico(request):

    if request.method == 'GET':

        id_audio = request.GET.get('id_audio')

        audio = Audio.objects.filter(
            id=id_audio).values_list('audio', flat=True)

        ruta_audio = os.path.join(MEDIA_ROOT, 'audio', audio[0])

        speech = sr.Recognizer()

        with sr.AudioFile(ruta_audio) as source:
            audio_data = speech.record(source)
            text = speech.recognize_google(audio_data, language='es')

        audio_url = os.path.join(
            MEDIA_URL, 'audio', audio[0]).replace("\\", "/")

        return JsonResponse({
            'audio_url': audio_url,
            'texto': text,
        })
