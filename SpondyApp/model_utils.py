import logging
import threading
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)
MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "cnn_weights.hdf5"
_model = None
_model_lock = threading.RLock()


def get_model():
    global _model

    if _model is not None:
        return _model

    with _model_lock:
        if _model is None:
            if not MODEL_PATH.is_file():
                raise FileNotFoundError("The configured CNN model file is missing.")

            import tensorflow as tf

            _model = tf.keras.models.load_model(str(MODEL_PATH), compile=False)
            logger.info("Loaded CNN model from %s", MODEL_PATH.name)

    return _model


def preprocess_image(image):
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("A decoded image is required.")

    resized = cv2.resize(image, (64, 64))
    normalized = resized.astype(np.float32) / 255.0
    return np.expand_dims(normalized, axis=0)


def is_valid_xray(image):
    if image is None or image.ndim != 3:
        return False

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return bool(grayscale.std() > 20)


def predict_image(image):
    with _model_lock:
        return get_model().predict(image, verbose=0)
