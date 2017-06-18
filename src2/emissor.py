#!/usr/bin/python3

from client import *

class Emissor(Client):
    def __init__(self, host='127.0.0.1', port=5000, exibidor_id=2**12):
        super().__init__(host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # o exibidor desejável para se conectar
        self.exibidor_id = exibidor_id

    def received_data(self, size):
        return super(Emissor, self).received_data(size)

    def receive_header(self):
        data = self.receive_data(Header.struct.size)
        return Header.struct.unpack(data)

    def start(self):
        if self.connect(self.exibidor_id):
            print_blue('Connected to remote host.')
        else:
            return False

        while True:
            socket_list = [sys.stdin, self.sock]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == self.sock:
                    data = self.receive_data()
                    if not data:
                        print_blue('\nDisconnected from chat server')
                        sys.exit()
                    self.manage_header(data)

                elif sock == sys.stdin:
                    msg = sys.stdin.readline()
                    if msg[:-1] == '/help':
                        # TODO: Do a help message
                        pass
                    elif msg[:-1] == '/status':
                        print_green('ID: ' + str(self.id))
                        print_green('socket_list: ' + str(socket_list))
                    elif msg[:-1] == '/exit':
                        sys.exit()
                    else:
                        self.send_data((msg_type.MSG, self.id, SERVER_ID, 0), msg)

def main(args):
    if(len(args) < 3) :
        print('Usage : python emissor.py <hostname> <port> <exibidor_id>')
        sys.exit()

    host = args[1]
    port = int(args[2])
    if len(args) >= 3:
        exibidor_id = int(args[3])
        emissor = Emissor(host=host, port=port, exibidor_id=exibidor_id)
    else:
        emissor = Emissor(host=host, port=port)

    emissor.start()


if __name__ == "__main__":
    main(sys.argv)
