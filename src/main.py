import cv2
import re
import imutils
import time
import numpy as np
import pytesseract
from imutils.perspective import four_point_transform
from PIL import Image, ImageOps
from pytesseract import Output
from pytesseract.pytesseract import string
import serial
import struct
import os

os.makedirs("test_images", exist_ok=True)
ser = serial.Serial("/dev/ttyUSB0", 115200)
# reset the ESP32 automatically
time.sleep(2)
# Throw away boot messages
ser.reset_input_buffer()


def main():
    print()
    print("Starting Process:")
    print()
    # image = cv2.imread("test_images/printed_sample.png")
    # image = cv2.imread("test_images/handwritten_sample_easy.png")
    # image = cv2.imread("test_images/10 random aresses PNG/page-10.png")
    ser.write(b"CAPTURE\n")
    filename = receivingSavingImage()
    image = cv2.imread(filename)
    if image is None:
        raise RuntimeError("Failed to load received image")
    # image = auto_rotate(image) #TODO: implement
    image = cv2_to_pil(image)  # switch to PIL here
    image = imageRotating(image)
    image = imageProcessing(image)
    testOutput(image)
    text = imageToText(image)
    result = processTextMichael(text)
    print()
    print("Result: \n")
    # printText(text)
    printText(result)


def wait_for_header():
    buffer = bytearray()

    while True:
        b = ser.read(1)

        if not b:
            continue

        buffer += b

        # keep only last 3 bytes
        if len(buffer) > 3:
            buffer = buffer[-3:]

        if buffer == b"IMG":
            print("Found IMG header")
            return


def receivingSavingImage():
    wait_for_header()
    # Read image size (4 bytes)
    length_bytes = ser.read(4)

    # Convert bytes to integer
    length = struct.unpack("<I", length_bytes)[0]

    print(f"Receiving image of {length} bytes")

    # Read the image
    image_data = ser.read(length)

    filename = "test_images/image.jpg"

    with open(filename, "wb") as f:
        f.write(image_data)

    print(f"Saved {filename}")
    return filename


def cv2_to_pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def imageRotating(image):
    # processing for better accuracy
    image = image.rotate(-90, expand=True)
    print("     Rotating Image...")
    return image


# still need to understand ts
def autoImageCutting(image):
    print("     Auto-Cutting Image...")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    page = max(cnts, key=cv2.contourArea)

    # Try for a clean quad, fall back to the rotated bounding rectangle
    peri = cv2.arcLength(page, True)
    approx = cv2.approxPolyDP(page, 0.02 * peri, True)
    if len(approx) == 4:
        quad = approx.reshape(4, 2)
    else:
        quad = cv2.boxPoints(cv2.minAreaRect(page)).astype("int32")

    warped = four_point_transform(image, quad)

    return warped


def imageProcessing(image):
    image = ImageOps.grayscale(image)
    image = image.resize((image.width * 3, image.height * 3))
    image = ImageOps.autocontrast(image)
    image = image.point(lambda p: 255 if p > 160 else 0)
    print("     Processing Image...")
    return image


def testOutput(image):
    # check how the processed image looks
    image.save("output_image/debug_output.png")
    print("     Saving Processed Image...")


def imageToText(image):
    # the actual converting of the image into text
    text = pytesseract.image_to_string(image)
    print("     Converting Image to Text...")
    return text


def processTextMichael(text):
    pattern = re.compile(r"A\n\n([A-Za-z]+ Omlid)\n\n", re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1) if match else None


def printText(text):
    print("     " + repr(text))


if __name__ == "__main__":
    main()
