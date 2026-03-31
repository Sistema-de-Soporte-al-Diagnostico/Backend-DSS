import os
import numpy as np
import tensorflow as tf
from typing import Tuple

# Calculamos la ruta absoluta hacia backend/ml_artifacts/modelo_fnn.h5
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml_artifacts", "modelo_fnn.h5")

# Variable global para mantener el modelo cargado en memoria
modelo_ia = None

# Carga del modelo al inicializar el módulo (una sola vez)
try:
    if os.path.exists(MODEL_PATH):
        # Usamos compile=False si solo vamos a hacer inferencia
        modelo_ia = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print(f"✅ Modelo de IA cargado exitosamente desde: {MODEL_PATH}")
    else:
        print(f"⚠️ Advertencia: No se encontró el modelo en la ruta {MODEL_PATH}. Las predicciones fallarán interactivamente.")
except Exception as e:
    print(f"❌ Error crítico al cargar el modelo de IA: {e}")

# Mapeo de ejemplo de las clases de salida de la Red Neuronal
CLASES_ENFERMEDAD = ["Sano", "Parvovirus", "Moquillo", "Leptospirosis", "Rabia"]

def predecir_enfermedad(datos_clinicos: dict) -> Tuple[str, float]:
    """
    Recibe un diccionario con los síntomas clínicos.
    Simula el preprocesamiento pasando los valores a un array de NumPy.
    Ejecuta el modelo predict() y retorna la enfermedad detectada junto a su probabilidad.
    """
    if modelo_ia is None:
        raise RuntimeError("El modelo de IA no está disponible. Verifique que 'modelo_fnn.h5' existe en 'ml_artifacts/'.")
    
    # 1. Preprocesamiento (Simulación)
    # Extraemos solo los valores numéricos del diccionario en el orden recibido.
    # NOTA: En producción, este orden debe ser estricto e igual al del entrenamiento.
    valores = list(datos_clinicos.values())
    
    # Convertimos los valores en un arreglo 2D de NumPy con tipo float32 (esperado por Keras)
    # Forma del array: (1, número_de_características)
    entrada_numpy = np.array([valores], dtype=np.float32)

    # 2. Inferencia con TensorFlow/Keras
    # predict() retorna un array con las probabilidades (ej. salida Softmax)
    prediccion_proba = modelo_ia.predict(entrada_numpy)
    
    # 3. Postprocesamiento de la predicción
    # Obtenemos el índice con la mayor probabilidad
    indice_clase = np.argmax(prediccion_proba[0])
    probabilidad = float(prediccion_proba[0][indice_clase])
    
    # Mapeamos el índice a nuestro listado de enfermedades
    if indice_clase < len(CLASES_ENFERMEDAD):
        enfermedad = CLASES_ENFERMEDAD[indice_clase]
    else:
        enfermedad = "Enfermedad no catalogada"
        
    return enfermedad, probabilidad
