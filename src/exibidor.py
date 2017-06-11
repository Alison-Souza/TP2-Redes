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
        what_type, id_origin, id_destiny, seq_num = extract_header(data)

        #if it's not for you, ignore
        if id_destiny != self.id or self.id != 0:
            print_error('Message not for you')
            print_error('id_destiny: ' + str(id_destiny))
            sys.exit()

        if what_type == msg_type.OK:
            print_blue('Receive OK from: ' + str(id_origin))
            print_blue('Seq number: ' + str(seq_num))
        elif what_type == msg_type.ERRO:
            print_error('ERRO returned from server')
        elif what_type == msg_type.FLW:
            # Aqui ele recebe o FLW do servidor, manda o OK de volta e fecha conexão
            print_blue('FLW received from server')
            # TODO: check message seq, now set to zero for XGH
            self.send_data((msg_type.OK, self.id, SERVER_ID, 0))
            self.sock.close()
            sys.exit()
        elif what_type == msg_type.MSG:
            # Recebe uma mensagem e printa na tela
            # TODO: o emissor vai printar a mensagem na tela?
            # TODO: se o DATA tiver mais dados? while True?
            print_blue('MSG for you, maybe!')
            data = self.receive_data()
            print(data)
        elif what_type == msg_type.CREQ:
            print_error('Wrong request CREQ, this is not for me!')
            print_error(header)
            sys.exit()
        elif what_type == msg_type.CLIST:
            # TODO: o emissor vai printar a mensagem na tela?
            # TODO: se o DATA tiver mais dados? while True?
            data = self.receive_data()
            print(data)
            # O cliente deve mandar uma mensgem de volta com OK
            self.send_data((msg_type.CLIST, self.id, SERVER_ID, 0), 'OK')

    def start(self):
        if self.try_connect(0) is not None:
            print_blue('Connected to remote host.')
        else:
            print_error('Error in trying to connect')
            sys.exit()

        while True:
            socket_list = [self.sock]
            print_green(1)

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
    if(len(args) < 3) :
        print('Usage : python exibidor.py <hostname> <port>')
        sys.exit()

    host = args[1]
    port = int(args[2])

    exibidor = Exibidor(host=host, port=port)
    exibidor.start()


if __name__ == "__main__":
    main(sys.argv)
