from utils import *

class Client:
    def __init__(self, host='127.0.0.1', port=5000):
        # super(Exibidor, self).__init__()
        # set values from default if not sent
        self.id = 0
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.seq_num = 0

    def get_id(self):
        return self.id

    # TODO: Olhar se vou realmente usar isso
    def set_id(self, number):
        self.id = number

    def __del__(self):
        if self.sock._closed == False:
            data = (msg_type.FLW, self.id, SERVER_ID, 0)
            self.send_data(data)
            while True:
                try:
                    print_blue('Waiting for OK from FLW...')
                    read_sockets, write_sockets, error_sockets = select.select([self.sock],[],[])
                    header, id_origin, id_destiny, dummy = self.receive_header()
                    if header == msg_type.OK and id_origin == SERVER_ID and id_destiny == self.id:
                        break
                except Exception as e:
                    print_error('Something wrong from receive FLW-OK')
                    break
                    # continue
        self.sock.close()
        print_blue('Client died!')

    def connect(self, request_id):
        print_warning('connect')
        try:
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(5)
            self.send_data((msg_type.OI, request_id, SERVER_ID, 0))
            # TODO: use select
            # time.sleep(1)
            what_type, id_origin, id_destiny, dummy = self.receive_header()
        except Exception as e:
            print_error('Error in trying to connect server')
            raise
            return False

        if what_type == msg_type.OK:
            self.id = id_destiny
            print_warning('DONE connect')
            return True
        else:
            return False


        # TODO: COntinuar depois do send_data

    # Constroi o cabecalho concatenado a mensagem em formato binario e envia pelo socket
    def send_data(self, header, data=''):
        print_warning('send_data')
        print_bold(header)
        if data is not '':
            print_bold(data)
        if header is not tuple:
            header = tuple(header)
        data = bytes(data, 'ascii')
        if len(data) > 0 or msg_type.MSG == header[0]:
            # for MSG tem que passar o tamanho (int 2  bytes) da mensagem
            # como quinto elemento da tupla
            header = (*header, len(data), data)
            struct_aux = struct.Struct('! H H H H H ' + str(len(data)) + 's')
        else:
            struct_aux = Header.struct
        b = ctypes.create_string_buffer(struct_aux.size)
        struct_aux.pack_into(b, 0, *header)
        print_bold(b.raw)
        try:
            self.sock.send(b)
        except:
            print_error('Erro in trying to send data')
            return False
        return True

    def receive_data(self, size):
        try:
            data = self.sock.recv(size)
            if not data :
                print_error('\nDisconnected from chat server')
                sys.exit()
        except:
            print_error('Error in receive data!')
            sys.exit()
        return data

    def receive_header(self):
        print_warning('receive_header')
        data = self.receive_data(Header.struct.size)
        print_bold(data)
        return Header.struct.unpack(data)

    def handle_ok(self, id_origin, seq_num):
        print_warning('Receive OK from: ' + str(id_origin))
        print_warning('Seq number: ' + str(seq_num))
        self.seq_num += 1

    def handle_erro(self, id_origin):
        print_error('ERRO returned from server ' + str(id_origin))
        # TODO: Esse erro tem que tratar todos os casos
        # erro no OI, MSG, etc

    def handle_flw(self):
        print_blue('FLW received from server')
        # TODO: check message seq, now set to zero for XGH
        self.send_data((msg_type.OK, self.id, SERVER_ID, 0))
        time.sleep(5)
        sys.exit()

    def handle_msg(self, id_origin, data):
        print_error('MSG received from '+ str(id_origin) + ', it\'s not for me!')

    def handle_creq(self, header):
        print_error('Wrong request CREQ, this is not for me!')
        print_error(header)
        sys.exit()

    def handle_clist(self, data):
        '''
        Essa mensagem possui um inteiro (2 bytes) indicando numero de clientes conectados, ´
        N. A mensagem CLIST possui tambem uma lista de ´ N inteiros (2 bytes cada) que armazena os
        identificadores de cada cliente (exibidor e emissor) conectador ao sistema.
        '''
        # TODO: o emissor vai printar a mensagem na tela?
        # TODO: se o DATA tiver mais dados? while True?
        print_green(data[self.head_struct.size:].decode('ascii'), end="")
        # O cliente deve mandar uma mensgem de volta com OK
        self.send_data((msg_type.CLIST, self.id, SERVER_ID, 0), 'OK')
