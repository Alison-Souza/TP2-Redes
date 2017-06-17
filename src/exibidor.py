#!/usr/bin/python3

from client import *

class Exibidor(Client):
    def __init__(self, **kwargs):
        super(Exibidor, self).__init__()
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def received_data(self):
        return super(Exibidor, self).received_data(self.sock)

    def manage_header(self, data):
        super(Exibidor, self).manage_header(data)

    def handle_ok(self, id_origin, seq_num):
        super(Exibidor, self).handle_ok(id_origin, seq_num)

    def handle_erro(self):
        super(Exibidor, self).handle_erro()

    def handle_flw(self):
        super(Exibidor, self).handle_flw()

    def handle_msg(self, id_origin, data):
        # TODO: o emissor vai printar a mensagem na tela?
        # TODO: se o DATA tiver mais dados? while True?
        if id_origin == SERVER_ID:
            print_green(data[self.head_struct.size:].decode('ascii'), end="")
        else:
            print_green('[id:' + str(id_origin) + ']> ' + data[self.head_struct.size:].decode('ascii'), end="") # DEBUG purpose

    def handle_creq(self, header):
        super(Exibidor, self).handle_creq(header)

    def handle_clist(self, data):
        super(Exibidor, self).handle_creq(data)

    def start(self):
        # TODO: make dynamic input od if . Example: 0
        if self.try_connect(0) is not None:
            print_blue('Connected to remote host.')
        else:
            print_error('Error in trying to connect')
            sys.exit()

        while True:
            socket_list = [self.sock]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == self.sock:
                    data = self.receive_data()
                    if not data :
                        print_blue('\nDisconnected from chat server')
                        sys.exit()
                    self.manage_header(data)

def main(args):
    if(len(args) < 3):
        print('Usage : python exibidor.py <hostname> <port>')
        sys.exit()

    host = args[1]
    port = int(args[2])

    exibidor = Exibidor(host=host, port=port)
    exibidor.start()


if __name__ == "__main__":
    main(sys.argv)
