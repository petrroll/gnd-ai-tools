import socket
import selectors
import types

import fire

class SocketReader():
    def __init__(self, host, port, sep = '\n'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        sock.setblocking(False)
        self.sock = sock

        sel = selectors.DefaultSelector()
        sel.register(sock, selectors.EVENT_READ, data=None)
        self.sel = sel
        self.sep = sep


    def service_connection(self, key, mask, selector, separator):
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:   # Receive chunk of data from socket -> transform to UTF8 string
                msg = recv_data.decode('utf-8')
                return msg
            else:           # Event happened (select fired) but no data -> error
                print('closing connection to', data.addr)
                selector.unregister(sock)
                sock.close()
                return None

    def accept_wrapper(self, sock, selector):
        conn, addr = sock.accept()
        print('accepted connection from', addr)

        conn.setblocking(False)
        selector.register(conn, selectors.EVENT_READ, data=addr)    # `data` to distinguish between connection & new to-accept in select (l:50)

    def produce(self):
        msg = ""
        sep = self.sep
        sel = self.sel
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj, sel)
                else:
                    dta = self.service_connection(key, mask, sel, sep)  # Get Chunk of data from socket
                    if not dta: return                                  # Socket is down / got no data / ... exit application
                    msg += dta

                    # Go through current msg buffer and yield one full message (delimetered) by one
                    sep_idx = msg.find(sep)
                    while sep_idx != -1:
                        currMsg, msg = msg[:sep_idx], msg[sep_idx+1:]   # Cut last finished message (up until first ';') -> yield it
                        yield currMsg                                   # Process the rest (could contain multiple messages)
                        sep_idx = msg.find(sep)
                        


def main(host='127.0.0.1', port=4444, sep='\n'):
    listener = SocketReader(host, port, sep)
    for i in listener.produce():
        print('>>>', i)


if __name__ == "__main__":
    fire.Fire(main)