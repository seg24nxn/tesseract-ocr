import pytesseract
import cv2
from pytesseract import TesseractError, Output


class Tesseract:
    @staticmethod
    def image_to_text_with_confidence(image):
        try:
            data = pytesseract.image_to_data(
                image,
                output_type=Output.DICT,
                config="--psm 3",
            )

            words = []
            confidences = []

            for text, conf in zip(
                data["text"],
                data["conf"],
                strict=False,
            ):
                text = text.strip()

                if text and int(conf) >= 0:
                    words.append(text)
                    confidences.append(int(conf))

            extracted_text = " ".join(words)

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return (
                extracted_text,
                avg_confidence,
                list(zip(words, confidences, strict=False)),
            )

        except TesseractError as e:
            print(f"Tesseract error: {e}")
            return "", 0, []
