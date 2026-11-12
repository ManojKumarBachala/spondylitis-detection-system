from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.urls import reverse


class PublicDemoTests(SimpleTestCase):
    def test_home_and_health_endpoints(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_invalid_upload_is_not_saved(self):
        response = self.client.post(
            reverse("predict"),
            {"image": SimpleUploadedFile("bad.png", b"not an image", content_type="image/png")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "readable JPEG or PNG image", status_code=400)
        self.assertFalse((Path(__file__).parent / "static" / "test.jpg").exists())

    @patch("SpondyApp.views.predict_image")
    def test_valid_upload_returns_model_output_without_saving_image(self, predict_image):
        image = np.zeros((64, 64, 3), dtype=np.uint8)
        image[:, 32:] = 255
        success, encoded = cv2.imencode(".png", image)
        self.assertTrue(success)
        predict_image.return_value = np.array([[0.2, 0.8]])

        response = self.client.post(
            reverse("predict"),
            {
                "image": SimpleUploadedFile(
                    "spine.png",
                    encoded.tobytes(),
                    content_type="image/png",
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spondylitis")
        self.assertContains(response, "80.0%")
        self.assertFalse((Path(__file__).parent / "static" / "test.jpg").exists())
