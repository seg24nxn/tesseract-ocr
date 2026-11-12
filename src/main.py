import subprocess
from pathlib import Path
import cv2

from electric import arduino_control
from electric.camera_control import CameraControl
from electric.arduino_control import ArduinoControl
from electric.electronic_connection import ElectronicConnections

from image_processing.picture_processor import PictureProcessor

from ocr.tesseract import Tesseract

from result_processing.result_processor import ResultProcessor


def capture_image(camera, ser):
    image = camera.take_picture(ser)

    if image is None:
        raise RuntimeError("Failed to capture image")

    return image


def preprocess_image(image):
    # image = PictureProcessor.crop_to_text(image)
    image = PictureProcessor.cv2_to_pil(image)
    # image = PictureProcessor.apply_filters(image)

    return image


def process_with_tesseract(image):
    image = preprocess_image(image)

    PictureProcessor.save_debug(
        image,
        "tesseract_debug.png",
    )

    print("Extracting Text...")
    text, confidence, word_data = Tesseract.image_to_text_with_confidence(image)
    print("Handing it to Result Matching")
    print()
    return text


def process_with_tesseract_big_output(image):
    image = preprocess_image(image)

    PictureProcessor.save_debug(
        image,
        "tesseract_debug.png",
    )

    text, confidence, word_data = Tesseract.image_to_text_with_confidence(image)

    print("\n=== TESSERACT RESULT ===")
    print(f"Text       : {text}")
    print(f"Confidence : {confidence:.1f}%")
    print()

    for word, conf in word_data:
        print(f"{word:<20} {conf:>3}%")

    print("========================\n")

    print("Handing it to Result Matching")
    print()
    ResultProcessor().process_text_extraction_output(text)


def process_with_trocr(image):
    from ocr.trocr import TrOCR

    image = preprocess_image(image)

    PictureProcessor.save_debug(
        image,
        "trocr_debug.png",
    )

    text = TrOCR.image_to_text(image)

    print("\n--- TrOCR Result ---")
    print(repr(text))
    print("--------------------\n")


def open_latest_image():
    subprocess.run(["xdg-open", str(Path("output_image/image.jpg").resolve())])


def pre_menu():

    arduinoSer = None
    cameraSer = None

    while True:
        print("\n========================")
        print("1 - Process printed sample")
        print("2 - Connect to Eletronics")
        print("q - Quit")
        print("\n========================")

        choice = input("Select option: ").strip().lower()
        try:
            if choice == "1":
                print("\nLoading sample...")

                # image = cv2.imread("test_images/OCR-Box-Images/self_06.jpg")
                image = cv2.imread("output_image/history/2026-11-05_12-31-56.jpg")

                if image is None:
                    print("Could not load image.")
                    continue

                process_with_tesseract_big_output(image)
                # process_with_trocr(image) # TODO: for improvement of general system

            elif choice == "2":
                print("\n Connecting to Eletronics...")
                eletronicConnector = ElectronicConnections()
                arduinoSer = eletronicConnector.connect_arduino()
                cameraSer = eletronicConnector.connect_camera()
                print(f"Arduino : {arduinoSer.port}")
                print(f"Camera  : {cameraSer.port}")
                camera = CameraControl()
                arduino = ArduinoControl()
                menu(camera, arduino, cameraSer, arduinoSer)

            elif choice == "q":
                print("Exiting...")

                if arduinoSer:
                    arduinoSer.close()
                if cameraSer:
                    cameraSer.close()

                break
            else:
                print("Invalid option.")

        except Exception as e:
            print(f"\nError: {e}\n")


def menu(camera, arduino, cameraSer, arduinoSer):

    while True:
        print("\n========================")
        print("-- Run the whole process")
        print("0 - For Running the whole program")
        print()
        print("-- Camera Debugging --")
        print("1 - Take image and show")
        print()
        print("-- Processing Debugging --")
        print("2 - Take image and process with Tesseract")
        print("3 - Take image and process with TrOCR")
        print("4 - Process printed sample")
        print()
        print("-- Eletronic Debugging --")
        print("5 - Test Arduino control")

        print("q - Quit")
        print("========================")

        choice = input("Select option: ").strip().lower()

        try:
            if choice == "0":
                print("\nStarting program")
                image = capture_image(camera, cameraSer)
                text = process_with_tesseract(image)
                number = ResultProcessor().process_text_extraction_output(text)
                ArduinoControl.i_like_to_move_it_move_it(arduinoSer, number)

            elif choice == "1":
                print("\nCapturing image...")
                capture_image(camera, cameraSer)
                open_latest_image()

            elif choice == "2":
                print("\nCapturing image...")
                image = capture_image(camera, cameraSer)
                process_with_tesseract_big_output(image)

            elif choice == "3":
                print("\nCapturing image...")
                image = capture_image(camera, cameraSer)
                process_with_trocr(image)

            elif choice == "4":
                print("\nLoading sample...")

                # image = cv2.imread("test_images/OCR-Box-Images/self_06.jpg")
                image = cv2.imread("output_image/history/2026-11-05_12-31-56.jpg")

                if image is None:
                    print("Could not load image.")
                    continue

                process_with_tesseract_big_output(image)
                # process_with_trocr(image) # TODO: for improvement of general system

            elif choice == "5":
                print("testing arduino_control...")
                while ElectronicConnections.health_check(arduinoSer):
                    choice = input("Choose a Compartment to Test: ").strip().lower()
                    ArduinoControl.i_like_to_move_it_move_it(arduinoSer, choice)

            elif choice == "q":
                print("Exiting...")

                if arduinoSer:
                    arduinoSer.close()
                if cameraSer:
                    cameraSer.close()

                break

            else:
                print("Invalid option.")

        except Exception as e:
            print(f"\nError: {e}\n")


def main():
    print("\nStarting process...\n")
    pre_menu()


if __name__ == "__main__":
    main()
