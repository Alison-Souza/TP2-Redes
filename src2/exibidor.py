#!/usr/bin/python3

from client import *

class Exibidor(Client):
    def __init__(self, host='127.0.0.1', port=5000):
        super(Exibidor, self).__init__(host, port)

    def received_data(self):
        return super(Exibidor, self).received_data()

    def receive_header(self):
        return super(Exibidor, self).receive_header()

    # def handle_ok(self, id_origin, seq_num):
    #     super(Exibidor, self).handle_ok(id_origin, seq_num)
    #
    # def handle_erro(self):
    #     super(Exibidor, self).handle_erro()
    #
    # def handle_flw(self):
    #     super(Exibidor, self).handle_flw()

    def handle_msg(self, id_origin, seq_num):
        try:
            length = struct.Struct('! H').unpack(self.receive_data(struct.Struct('! H').size))
            struct_string = struct.Struct('! ' + str(length) + 's')
            data = struct_string.unpack(self.receive_data(struct_string.size))
        except:
            print_error('Error in receive message')
            raise
        if id_origin == SERVER_ID:
            print_green(data.decode('ascii'), end="")
        else:
            print_green('[id:' + str(id_origin) + ']> ' + data.decode('ascii'), end="") # DEBUG purpose

    # def handle_creq(self, header):
    #     super(Exibidor, self).handle_creq(header)

    # def handle_clist(self, data):
    #     super(Exibidor, self).handle_creq(data)

    def start(self):
        # TODO: make dynamic input od if . Example: 0
        if self.connect(0):
            print_blue('Connected to remote host.')
        else:
            print_error('Error in trying to connect')
            sys.exit()

        while True:
            # Get the list sockets which are readable
            select.select([self.sock] , [], [])
                #incoming message from remote server
            header = self.receive_header()
            if not header:
                print_blue('\nDisconnected from chat server')
                sys.exit()
            if len(header) != 4:
                print_error('Error in receive_header')
                sys.exit()

            what_type, id_origin, id_destiny, seq_num = header

            if what_type == msg_type.OK:
                # Toda as mensagens tem que ter um OK. O envio de uma mensagem de
                # OK nao incrementa o numero de sequencia das mensagens do cliente (mensagens de OK nao tem
                # numero de sequencia proprio
                # self.handle_ok()
                pass
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
                else:
                    print_error('Message not for me')
            elif what_type == msg_type.CREQ:
                pass
            elif what_type == msg_type.CLIST:
                # uma chatice, leia documentacao, no final o cliente responde OK
                pass
            else:
                print_error('Impossible situation!\nPray for modern gods of internet!')
                print_error('Type: ' + str(what_type))
                return

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
