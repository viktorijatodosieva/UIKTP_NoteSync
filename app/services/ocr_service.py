import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO
from textblob import TextBlob


class OCRService:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def preprocess_image(self, img_bytes):
        img_pil = Image.open(BytesIO(img_bytes)).convert("RGB")
        enhancer = ImageEnhance.Contrast(img_pil)
        img_pil = enhancer.enhance(2.0)

        image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.bilateralFilter(gray, 11, 17, 17)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        return thresh

    def extract_raw_text(self, image_file):
        try:
            img_bytes = image_file.read()
            processed_img = self.preprocess_image(img_bytes)
            results = self.reader.readtext(processed_img, detail=0)
            return "\n".join(results) if results else ""
        except Exception as e:
            print(f"OCR Error (raw): {str(e)}")
            return ""

    def correct_text(self, text):
        try:
            blob = TextBlob(text)
            return str(blob.correct())
        except Exception as e:
            return text

    def extract_text(self, image_file):
        raw = self.extract_raw_text(image_file)
        return self.correct_text(raw)
