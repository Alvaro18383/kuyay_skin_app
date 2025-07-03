import cv2
import numpy as np
from PIL import Image
import hashlib


def es_rostro_valido(imagen):
    """Valida si hay rostro humano real en la imagen."""
    img = np.array(imagen.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Cargar el clasificador de rostro
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    rostros = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # ✅ Condición 1: debe detectar al menos un rostro
    hay_rostro = len(rostros) > 0

    # ✅ Condición 2: la imagen debe tener suficiente variación (para que no sea un fondo plano)
    variacion = img.std() > 60

    if hay_rostro and variacion:
        return True
    else:
        return False


def analizar_piel(imagen):
    """Análisis de piel consistente usando hash."""

    img = np.array(imagen.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    hash_imagen = hashlib.md5(img).hexdigest()

    tipos_piel = ["Grasa", "Seca", "Mixta", "Sensible", "Deshidratada", "Rosácea", "Normal"]
    indice = int(hash_imagen, 16) % len(tipos_piel)
    tipo_piel = tipos_piel[indice]

    descripciones = {
        "Grasa": "Tu piel presenta brillo, poros dilatados y tendencia a brotes. Necesita control de sebo y limpieza constante.",
        "Seca": "Tu piel se siente tirante, áspera y opaca. Necesita mucha hidratación y productos ricos en lípidos.",
        "Mixta": "Tienes zonas grasas (frente, nariz, mentón) y zonas secas (mejillas). Necesitas equilibrar ambas zonas.",
        "Sensible": "Tu piel reacciona con facilidad ➝ rojeces, ardor, picor. Necesita calma y fortalecimiento de la barrera cutánea.",
        "Deshidratada": "Tu piel carece de agua ➝ sensación de tirantez, pero puede lucir grasa. Necesita hidratación intensiva.",
        "Rosácea": "Tu piel presenta enrojecimiento constante, sensibilidad y a veces granitos. Necesita cuidado extremadamente suave.",
        "Normal": "Tu piel está equilibrada ➝ sin exceso de grasa ni resequedad. ¡Sigue cuidándola para mantenerla saludable!"
    }

    descripcion = descripciones[tipo_piel]

    return tipo_piel, descripcion
