import cv2
from pathlib import Path
from imutils.perspective import four_point_transform
from PIL import Image, ImageOps


class PictureProcessor:
    @staticmethod
    def cv2_to_pil(image):
        return Image.fromarray(
            cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB,
            )
        )

    @staticmethod
    def apply_filters(image):
        image = ImageOps.grayscale(image)
        image = image.resize(
            (
                image.width * 3,
                image.height * 3,
            )
        )
        image = ImageOps.autocontrast(image)

        return image

    @staticmethod
    def save_debug(image, filename):
        Path("output_image").mkdir(exist_ok=True)

        image.save(f"output_image/{filename}")

    @staticmethod
    def crop_to_text(image):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        _, thresh = cv2.threshold(
            gray,
            200,
            255,
            cv2.THRESH_BINARY_INV,
        )

        coords = cv2.findNonZero(thresh)

        if coords is None:
            return image

        x, y, w, h = cv2.boundingRect(coords)

        padding = 20

        x = max(0, x - padding)
        y = max(0, y - padding)

        w = min(
            image.shape[1] - x,
            w + 2 * padding,
        )

        h = min(
            image.shape[0] - y,
            h + 2 * padding,
        )

        return image[
            y : y + h,
            x : x + w,
        ]
