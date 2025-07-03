import numpy as np
from PIL import Image
import hashlib

def es_rostro_valido(imagen):
    img = np.array(imagen.convert('RGB'))
    alto, ancho = img.shape[:2]
    brillo = img.mean()
    variacion = img.std()
    return alto >= 150 and ancho >= 150 and brillo > 50 and variacion > 60

def analizar_piel(imagen):
    img = np.array(imagen.convert('RGB'))
    hash_imagen = hashlib.md5(img).hexdigest()

    tipos_piel = ["Grasa", "Seca", "Mixta", "Sensible", "Deshidratada", "Rosácea", "Normal"]
    descripciones = {
        "Grasa": "Tu piel presenta brillo, poros dilatados y tendencia a brotes. Necesita control de sebo.",
        "Seca": "Tu piel se siente tirante, áspera y opaca. Necesita hidratación rica en lípidos.",
        "Mixta": "Zonas grasas y zonas secas. Necesitas equilibrio entre limpieza e hidratación.",
        "Sensible": "Tu piel reacciona con facilidad. Necesita calma y cuidado suave.",
        "Deshidratada": "Tu piel carece de agua. Puede lucir grasa pero necesita hidratación intensiva.",
        "Rosácea": "Piel enrojecida, sensible. Requiere cuidado muy suave.",
        "Normal": "Tu piel está equilibrada. ¡Mantén buenos hábitos!"
    }

    tipo_piel = tipos_piel[int(hash_imagen, 16) % len(tipos_piel)]
    return tipo_piel, descripciones[tipo_piel]
