from utils import *

class Client:
    def __init__(self):
        # set values from default if not sent
        self.head_struct = struct.Struct('! H H H H')
        self.id = 0

    def getId(self):
        return self.id

    def __del__(self):
        self.send_data(msg_type.FLW, self.id, SERVER_ID, 0)
        while(True):
            try:
                data = self.receive_data(RECV_BUFFER)
            except:
                continue
            header = self.extract_header(data)
            if header[0] != msg_type.OK:
                continue
            else:
                break
        self.sock.close()
        print_error('Client died!')

    def try_connect(self, id):
        try:
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(5)
        except:
            print_error('Error in connect server')
            return None
        self.send_data((msg_type.OI, id, 0, 0))
        data = self.sock.recv(RECV_BUFFER)
        print_warning(data)
        message_type, id_origin, id_destiny, seq_num = self.extract_header(data)
        if message_type == msg_type.OK:
            self.id = id_destiny
            print_warning('Receive OK from: ' + str(id_origin))
            print_warning('Seq number: ' + str(seq_num))
            return True
        else:
            print_error('Expect msg_type.OK but is ' + str(data))
            return None

    def send_data(self, header, data=''):
        if header is not tuple:
            header = tuple(header)
        data = bytes(data, 'ascii')
        try:
            if len(data) > 0:
                header = (*header, data)
                struct_aux = struct.Struct('! H H H H ' + str(len(data)) + 's')
            else:
                struct_aux = self.head_struct

            b = ctypes.create_string_buffer(struct_aux.size)
            struct_aux.pack_into(b, 0, *header)
            print_bold(b.raw)
            self.sock.send(b)
        except:
            print_error('Deu merda em send_data')
            raise

    def extract_header(self, data):
        if len(data) < self.head_struct.size:
            print_error('Wrong size of header')
            print_error(data)
            return None
        data = data[:self.head_struct.size]
        unpacked_data = self.head_struct.unpack(data)
        # Print head in hex
        b = ctypes.create_string_buffer(self.head_struct.size)
        self.head_struct.pack_into(b, 0, *unpacked_data)
        print_bold(b.raw)

        return unpacked_data

    def receive_data(self):
        try:
            data = self.sock.recv(RECV_BUFFER)
            if not data :
                print_error('\nDisconnected from chat server')
                sys.exit()
        except:
            print_error('Error in receive data!')
            sys.exit()
        return data

    def manage_header(self, data):
        what_type, id_origin, id_destiny, seq_num = self.extract_header(data)

        #if it's not for you, ignore
        if id_destiny != self.id and self.id != 0:
            print_error('Message not for you')
            print_error('id_destiny: ' + str(id_destiny))
            print_error('Remember who you are ' + str(self.id))

        elif what_type == msg_type.OK:
            self.handle_ok(id_origin, seq_num)
        elif what_type == msg_type.ERRO:
            self.handle_erro()
        elif what_type == msg_type.FLW:
            # Aqui ele recebe o FLW do servidor, manda o OK de volta e fecha conexão
            self.handle_flw()
        elif what_type == msg_type.MSG:
            # Recebe uma mensagem e printa na tela
            self.handle_msg(id_origin, data)
        elif what_type == msg_type.CREQ:
            self.handle_creq(header)
        elif what_type == msg_type.CLIST:
            self.handle_clist(data)

    def handle_ok(self, id_origin, seq_num):
        print_warning('Receive OK from: ' + str(id_origin))
        print_warning('Seq number: ' + str(seq_num))

    def handle_erro(self):
        print_error('ERRO returned from server')

    def handle_flw(self):
        print_blue('FLW received from server')
        # TODO: check message seq, now set to zero for XGH
        self.send_data((msg_type.OK, self.id, SERVER_ID, 0))
        sys.exit()

    def handle_msg(self, id_origin, data):
        print_error('MSG received, it\'s not for me!')
        pass

    def handle_creq(self, header):
        print_error('Wrong request CREQ, this is not for me!')
        print_error(header)
        sys.exit()

    def handle_clist(self, data):
        # TODO: o emissor vai printar a mensagem na tela?
        # TODO: se o DATA tiver mais dados? while True?
        print_green(data[self.head_struct.size:].decode('ascii'), end="")
        # O cliente deve mandar uma mensgem de volta com OK
        self.send_data((msg_type.CLIST, self.id, SERVER_ID, 0), 'OK')
