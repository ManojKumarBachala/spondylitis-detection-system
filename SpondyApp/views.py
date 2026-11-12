import logging
from io import BytesIO

import cv2
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods
from PIL import Image, UnidentifiedImageError

from .model_utils import is_valid_xray, predict_image, preprocess_image

logger = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000


@require_GET
def index(request):
    return render(request, "index.html")


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


@require_http_methods(["GET", "POST"])
def predict(request):
    if request.method == "GET":
        return render(request, "Predict.html")

    uploaded_file = request.FILES.get("image")
    if uploaded_file is None:
        return render(
            request,
            "Predict.html",
            {"message": "Choose a spine X-ray image to continue."},
            status=400,
        )

    if uploaded_file.size > MAX_UPLOAD_SIZE:
        return render(
            request,
            "Predict.html",
            {"message": "The image must be 8 MiB or smaller."},
            status=413,
        )

    contents = uploaded_file.read()
    try:
        with Image.open(BytesIO(contents)) as uploaded_image:
            width, height = uploaded_image.size
            if width * height > MAX_IMAGE_PIXELS:
                return render(
                    request,
                    "Predict.html",
                    {"message": "The image dimensions are too large to process."},
                    status=400,
                )
            if uploaded_image.format not in {"JPEG", "PNG"}:
                raise ValueError("Only JPEG and PNG images are supported.")
            uploaded_image.verify()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, ValueError):
        return render(
            request,
            "Predict.html",
            {"message": "Choose a readable JPEG or PNG image."},
            status=400,
        )

    image = cv2.imdecode(np.frombuffer(contents, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return render(
            request,
            "Predict.html",
            {"message": "The uploaded file is not a readable image."},
            status=400,
        )

    if not is_valid_xray(image):
        return render(
            request,
            "Predict.html",
            {"message": "Please choose a clear spine X-ray image."},
            status=400,
        )

    try:
        scores = np.asarray(predict_image(preprocess_image(image)))
    except Exception:
        logger.exception("CNN inference failed")
        return render(
            request,
            "Predict.html",
            {"message": "The model is temporarily unavailable. Please try again later."},
            status=503,
        )

    if scores.shape != (1, 2) or not np.isfinite(scores).all():
        logger.error("CNN returned an invalid prediction shape: %s", scores.shape)
        return render(
            request,
            "Predict.html",
            {"message": "The model returned an invalid result."},
            status=503,
        )

    labels = ("Normal", "Spondylitis")
    predicted_index = int(np.argmax(scores[0]))
    return render(
        request,
        "Predict.html",
        {
            "prediction": labels[predicted_index],
            "confidence": round(float(scores[0][predicted_index]) * 100, 2),
        },
    )
