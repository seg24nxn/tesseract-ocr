import struct
from pathlib import Path
from datetime import datetime
import cv2
import time

import serial
from serial.tools import list_ports


class CameraControl:
    PORT = "/dev/ttyUSB0"
    BAUDRATE = 115200

    @staticmethod
    def create_connection_to_esp32():
        print("Waiting for camera...")

        while True:
            ports = [p.device for p in list_ports.comports()]

            if CameraControl.PORT in ports:
                print("Camera connected")

                ser = serial.Serial(
                    CameraControl.PORT,
                    CameraControl.BAUDRATE,
                    timeout=1,
                )

                ser.reset_input_buffer()
                return ser

            time.sleep(1)

    @staticmethod
    def take_picture(ser):
        if ser is None:
            raise RuntimeError("No serial connection")

        # Clear any stale serial data
        ser.reset_input_buffer()

        ser.write(b"CAPTURE\n")
        ser.flush()

        return CameraControl.receive_and_save_image(ser)

    @staticmethod
    def receive_and_save_image(ser):
        if ser is None:
            raise RuntimeError("No serial connection")

        print("Waiting for image...")

        CameraControl.wait_for_header(ser)

        length_bytes = ser.read(4)

        if len(length_bytes) != 4:
            raise RuntimeError(
                f"Expected 4-byte length header, got {len(length_bytes)}"
            )

        length = struct.unpack("<I", length_bytes)[0]

        print(f"Receiving {length} bytes")

        image_data = bytearray()

        while len(image_data) < length:
            chunk = ser.read(min(4096, length - len(image_data)))

            if not chunk:
                raise RuntimeError(
                    f"Transfer stopped at {len(image_data)}/{length} bytes"
                )

            image_data.extend(chunk)

        output_dir = Path("output_image")
        history_dir = output_dir / "history"

        output_dir.mkdir(exist_ok=True)
        history_dir.mkdir(exist_ok=True)

        current_image = output_dir / "image.jpg"

        # Move existing image to history
        if current_image.exists():
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            history_image = history_dir / f"{timestamp}.jpg"
            current_image.rename(history_image)
            print(f"Archived previous image -> {history_image}")

        # Save new image
        with open(current_image, "wb") as f:
            f.write(image_data)

        print(f"Saved {current_image}")

        return cv2.imread(str(current_image))

    @staticmethod
    def wait_for_header(ser):
        buffer = bytearray()

        while True:
            b = ser.read(1)

            if not b:
                continue

            buffer += b

            if len(buffer) > 3:
                buffer = buffer[-3:]

            if buffer == b"IMG":
                return
