from utils import *

class Client:
    def __init__(self):
        # set values from default if not sent
        self.head_struct = struct.Struct('! H H H H')
        self.id = 0

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
            return False
        self.send_data((msg_type.OI, id, 0, 0))
        data = self.sock.recv(RECV_BUFFER)
        print_warning(data)
        # TODO: if return ERRO, return False
        return True

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
            else :
                #print data
                sys.stdout.write(data)
                self.prompt()
        except:
            print_error('Error in receive data! MSG type.')
            sys.exit()
        return data
