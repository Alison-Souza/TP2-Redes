#!/usr/bin/python3

from client import *

class Exibidor(Client):
    def __init__(self, **kwargs):
        super(Exibidor, self).__init__()
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        pass

def main(args):
    if(len(args) < 3) :
        print('Usage : python exibidor.py <hostname> <port>')
        sys.exit()

    host = args[1]
    port = int(args[2])

    exibidor = Exibidor(host=host, port=port)
    exibidor.start()


if __name__ == "__main__":
    main(sys.argv)
