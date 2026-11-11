import cv2
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from transformers import logging


class TrOCR:
    logging.set_verbosity_error()
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

    @staticmethod
    def image_to_text(image):
        print("     Extracting Text from Image...")
        image = image.convert("RGB")
        try:
            pixel_values = TrOCR.processor(
                images=image, return_tensors="pt"
            ).pixel_values

            generated_ids = TrOCR.model.generate(pixel_values, max_new_tokens=100)

            text = TrOCR.processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]

            print("RESULT:", repr(text))
            print("LENGTH:", len(text))

            return text

        except Exception as e:
            print(f"TrOCR error: {e}")
            return None
