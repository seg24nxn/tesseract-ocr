class ArduinoControl:
    # https://youtu.be/hdcTmpvDO0I
    @staticmethod
    def i_like_to_move_it_move_it(ser, compartment_number):

        # Clear any stale serial data
        ser.reset_input_buffer()

        ser.write(f"{compartment_number}\n".encode())
        ser.flush()

        return ArduinoControl.wait_for_ready(ser)

    @staticmethod
    def wait_for_ready(ser):
        buffer = bytearray()

        while True:
            b = ser.read(1)

            if not b:
                continue

            buffer += b

            if len(buffer) > 5:
                buffer = buffer[-5:]

            if buffer == b"READY":
                print("Arduino is Ready again...")
                return
