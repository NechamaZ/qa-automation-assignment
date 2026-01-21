from socket import socket, AF_INET, SOCK_STREAM


def request_current_from_ammeter(port: int, command: bytes) -> float:
    """
    Sends a measurement request to the ammeter emulator and returns
    the measured current as a float.

    Returning the value (instead of only printing it) enables automated
    sampling, statistical analysis, and result management.
    """
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(command)
        data = s.recv(1024)

        if not data:
            raise RuntimeError("No data received from ammeter")
        value = float(data.decode('utf-8'))
        print(f"Received current measurement from port {port}: {value} A")
        return value
