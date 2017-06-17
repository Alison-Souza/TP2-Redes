#!/usr/bin/python3

from client import *

class Emissor(Client):
    def __init__(self, **kwargs):
        super().__init__()
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def received_data(self):
        return super(Emissor, self).received_data(self.sock)

    def manage_header(self, data):
        super(Emissor, self).manage_header(data)

    def handle_ok(self, id_origin, seq_num):
        super(Exibidor, self).handle_ok(id_origin, seq_num)

    def handle_erro(self):
        super(Exibidor, self).handle_erro()

    def handle_flw(self):
        super(Exibidor, self).handle_flw()

    def handle_msg(self, id_origin, data):
        super(Exibidor, self).handle_msg(id_origin, data)

    def handle_creq(self, header):
        super(Exibidor, self).handle_creq(header)

    def handle_clist(self, data):
        super(Exibidor, self).handle_creq(data)

    def start(self):
        # TODO: make dynamic input od if . Example: 2**12
        if self.try_connect(2**12) is not None:
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
                        # TODO: send FLW to all clients
                        sys.exit()
                    else:
                        self.send_data((msg_type.MSG, self.id, SERVER_ID, 0), msg)

def main(args):
    if(len(args) < 3) :
        print('Usage : python emissor.py <hostname> <port>')
        sys.exit()

    host = args[1]
    port = int(args[2])

    emissor = Emissor(host=host, port=port)
    emissor.start()


if __name__ == "__main__":
    main(sys.argv)
