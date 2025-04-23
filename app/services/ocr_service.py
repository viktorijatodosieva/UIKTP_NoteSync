import easyocr
import cv2
import numpy as np


class OCRService:
    def __init__(self):

        self.reader = easyocr.Reader(['en'])

    def extract_text(self, image_file):

        try:

            img_bytes = image_file.read()
            img_np = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)


            results = self.reader.readtext(image, detail=0)
            return "\n".join(results) if results else None

        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return None
