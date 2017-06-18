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
        return super(Emissor, self).receive_header()

    def handle_ok(self, id_origin, seq_num):
        print_warning('Receive OK from: ' + str(id_origin))
        print_warning('Seq number: ' + str(seq_num))
        if seq_num == self.seq_num:
            self.seq_num += 1

    def handle_msg(self, id_origin, seq_num):
        pass

    def start(self):
        if self.connect(self.exibidor_id):
            # print_blue('Connected to remote host.')
        else:
            return False

        while True:
            socket_list = [sys.stdin, self.sock]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == self.sock:
                    header = self.receive_header()
                    if not header:
                        continue

                    what_type, id_origin, id_destiny, seq_num = header

                    if what_type == msg_type.OK:
                        self.handle_ok(id_origin, seq_num)
                    elif what_type == msg_type.ERRO:
                        # igual ao OK mas indicando que alguma coisa deu errado
                        # self.handle_erro()
                        pass
                    elif what_type == msg_type.FLW:
                        # self.handle_flw()
                        pass
                    elif what_type == msg_type.MSG:
                        if id_destiny == self.id:
                            self.handle_msg(id_origin, seq_num)
                    elif what_type == msg_type.CLIST:
                        # O CLIST requisitado vai ao exibidor
                        pass
                    else:
                        print_error('Impossible situation!\nPray for modern gods of internet!')
                        print_error('Type: ' + str(what_type))
                        continue

                elif sock == sys.stdin:
                    msg = sys.stdin.readline()
                    if msg[:-1] == '/help':
                        # TODO: Do a help message
                        pass
                    elif msg[:-1] == '/list':
                        try:
                            header = (msg_type.CREQ, self.id, 0, 0)
                            self.send_data(header)
                        except Exception as e:
                            raise
                    elif msg[:-1] == '/status':
                        print_green('ID: ' + str(self.id))
                        print_green('socket_list: ' + str(socket_list))
                    elif msg[:-1] == '/exit':
                        sys.exit()
                    else:
                        self.send_data((msg_type.MSG, self.id, 0, self.seq_num), msg)

def main(args):
    if(len(args) < 3) :
        print('Usage : python emissor.py <hostname> <port> <exibidor_id>')
        sys.exit()

    host = args[1]
    port = int(args[2])
    if len(args) > 3:
        exibidor_id = int(args[3])
        emissor = Emissor(host=host, port=port, exibidor_id=exibidor_id)
    else:
        emissor = Emissor(host=host, port=port)
    emissor.start()

def test(args):
    if len(args) > 1:
        exibidor_id = int(args[1])
        emissor = Emissor(exibidor_id=exibidor_id)
    else:
        emissor = Emissor()

    emissor.start()

if __name__ == "__main__":
    # main(sys.argv)
    test(sys.argv)
