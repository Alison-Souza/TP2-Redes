# From Python 2.6 you can import the print function from Python 3:
from __future__ import print_function
import socket
import select
import sys

import struct
import binascii

class Client:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        # TODO: will send FLW if a person use ctrl+c
        self.sock.send('FLW')
        self.sock.close()
        print('died')

    def start(self):
        try:
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(5)
        except:
            print('Unable to connect')
            raise
        print('Connected to remote host. Start sending messages')

        while True:
            socket_list = [sys.stdin, self.sock]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == self.sock:
                    data = sock.recv(4096)
                    if not data :
                        print('\nDisconnected from chat server')
                        sys.exit()
                    else :
                        #print data
                        sys.stdout.write(data)
                        self.prompt()

                #user entered a message
                else :
                    msg = sys.stdin.readline()
                    self.sock.send(msg)
                    self.prompt()

    def prompt(self):
        sys.stdout.write('<Me> ')
        sys.stdout.flush()

def main(args):
    if(len(args) < 3) :
        print('Use only with Python2')
        print('Usage : python client.py <hostname> <port>')
        sys.exit()

    host = args[1]
    port = int(args[2])

    client = Client(host=host, port=port)
    client.start()

if __name__ == "__main__":
    main(sys.argv)
