import socket
import selectors
import types

import fire

class SocketWriter():
    def __init__(self, host, port, sep='\n'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.setblocking(True)
        self.sock = sock
        self.sep = sep


    def consume(self, msg):
        sep = self.sep
        self.sock.sendall((msg + sep).encode('utf-8'))

def main(host='127.0.0.1', port=4444, sep='\n'):
    reader = SocketWriter(host, port, sep)
    while True:
        msg = input("<<<")
        reader.consume(msg)

if __name__ == "__main__":
    fire.Fire(main)