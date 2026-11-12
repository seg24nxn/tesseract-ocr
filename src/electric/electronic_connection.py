import time
import serial
from serial.tools import list_ports


class ElectronicConnections:
    CAMERA_BAUDRATE = 115200
    ARDUINO_BAUDRATE = 9600

    @staticmethod
    def find_serial_device(identifier: str):
        """
        Search connected serial devices by description.

        Examples:
            find_serial_device("CP210")
            find_serial_device("Arduino")
        """
        for port in list_ports.comports():
            if identifier.lower() in port.description.lower():
                return port.device

        return None

    @staticmethod
    def connect_camera():
        print("Waiting for camera...")

        while True:
            device = ElectronicConnections.find_serial_device("CP210")

            if device:
                try:
                    ser = serial.Serial(
                        device,
                        ElectronicConnections.CAMERA_BAUDRATE,
                        timeout=1,
                    )

                    ser.reset_input_buffer()

                    print(f"Camera connected on {device}")
                    return ser

                except serial.SerialException as e:
                    print(f"Failed to connect: {e}")

            time.sleep(1)

    @staticmethod
    def connect_arduino():
        print("Waiting for Arduino...")

        while True:
            device = ElectronicConnections.find_serial_device("Arduino")

            if device:
                try:
                    ser = serial.Serial(
                        device,
                        ElectronicConnections.ARDUINO_BAUDRATE,
                        timeout=1,
                    )

                    ser.reset_input_buffer()

                    print(f"Arduino connected on {device}")
                    return ser

                except serial.SerialException as e:
                    print(f"Failed to connect: {e}")

            time.sleep(1)

    @staticmethod
    def health_check(ser):
        """
        Basic health check.
        """
        if ser is None:
            return False

        try:
            return ser.is_open

        except serial.SerialException:
            return False

    @staticmethod
    def reconnect_camera(current_connection):
        if ElectronicConnections.health_check(current_connection):
            return current_connection

        print("Camera disconnected. Reconnecting...")
        return ElectronicConnections.connect_camera()
