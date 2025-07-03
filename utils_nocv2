import numpy as np
from PIL import Image
import hashlib


def es_rostro_valido(imagen):
    """Simula validación de rostro sin usar OpenCV (compatible con Streamlit Cloud)."""
    img = np.array(imagen.convert('RGB'))
    alto, ancho = img.shape[:2]

    brillo = img[:, :, :3].mean()
    variacion = img.std()

    # Validaciones mínimas: imagen suficientemente grande, con luz y contraste
    if alto >= 150 and ancho >= 150 and brillo > 50 and variacion > 60:
        return True
    else:
        return False


def analizar_piel(imagen):
    """Devuelve un tipo de piel fijo basado en el hash para que sea consistente."""

    img = np.array(imagen.convert('RGB'))
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
