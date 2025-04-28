import base64


class Protocol:
    SERVER = ("127.0.0.1", 5656)
    DELIMITER = "|"

    @staticmethod
    def get_analyzed_data(client_socket):
        datasize = client_socket.recv(1)
        if datasize == b"":
            return None
        datasize = datasize.decode()
        while datasize[-1] != Protocol.DELIMITER:
            datasize += client_socket.recv(1).decode()
        datasize = int(datasize[:-1])
        b64data = b''
        for i in range(datasize):
            b64data += client_socket.recv(1)
        data = base64.b64decode(b64data)
        return data

    @staticmethod
    def create_message(data):
        if type(data) is str:
            data = data.encode()
        b64data = base64.b64encode(data)
        return f"{len(b64data)}{Protocol.DELIMITER}".encode() + b64data
