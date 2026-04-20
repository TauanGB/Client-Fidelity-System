from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from core.image_specs import validate_image_requirements


def png_file(name, width, height):
    header = b"\x89PNG\r\n\x1a\n"
    ihdr_length = (13).to_bytes(4, "big")
    ihdr = b"IHDR" + width.to_bytes(4, "big") + height.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00"
    fake_crc = b"\x00\x00\x00\x00"
    payload = header + ihdr_length + ihdr + fake_crc
    return SimpleUploadedFile(name, payload, content_type="image/png")


class ImageSpecValidationTests(SimpleTestCase):
    def test_logo_accepts_valid_square_png(self):
        upload = png_file("logo.png", 512, 512)
        self.assertEqual(validate_image_requirements(upload, "company_logo"), upload)

    def test_logo_rejects_small_png(self):
        upload = png_file("logo.png", 200, 200)
        with self.assertRaises(ValidationError):
            validate_image_requirements(upload, "company_logo")

    def test_banner_rejects_wrong_ratio(self):
        upload = png_file("banner.png", 900, 900)
        with self.assertRaises(ValidationError):
            validate_image_requirements(upload, "company_banner")
