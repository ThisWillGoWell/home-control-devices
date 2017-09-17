

import socket

class serverSocket:
    SERVER_URL = 'http://localhost/ws'
    sock = None

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sockSERVER
        self.connet()

    def connet(self):
        self.sock.connect((self.SERVER_URL,8080))

    def send(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent


    def get(self, system, what, otherParams):
        lst = {'op': 'get', 'system' : system, 'what' : what}
        for param in otherParams:
            lst[param] = otherParams[param]

        self.send(json.dumps(lst))

    def set(self, system, what,to, otherParams):
        lst = {'op': 'set', 'system' : system, 'what' : what, 'to':to}
        for param in otherParams:
            lst[param] = otherParams[param]

        self.send(json.dumps(lst))  


    def receive(self):
        chunks = []
        bytes_recd = 0
        validJson = False
        while not validJson:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
            print(''.join(chunks))
            try:
                json.loads(''.join(chunks))
                validJson = True
            except Exception as e:
                raise e

        return ''.join(chunks)


def main():
    s = serverSocket()
    while(True):
        s.receive()



if __name__ == '__main__':
    main()