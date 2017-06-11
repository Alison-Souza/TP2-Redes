from utils import *

class Client:
    def __init__(self):
        # set values from default if not sent
        self.head_struct = struct.Struct('! H H H H')
        self.id = 0

    def getId(self):
        return self.id

    def __del__(self):
        # TODO: will send FLW if a person use ctrl+c
        # self.sock.send('FLW')
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
            print_blue('Receive OK from: ' + str(id_origin))
            print_blue('Seq number: ' + str(seq_num))
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
        print_bold(binascii.hexlify(b.raw))

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
