from utils import *

class Client:
    def __init__(self, **kwargs):
        # set values from default if not sent
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.head_struct = struct.Struct('! H H H H')

    def __del__(self):
        # TODO: will send FLW if a person use ctrl+c
        # self.sock.send('FLW')
        self.sock.close()
        print('Client died')

    def send_header(self, values):
        try:
            b = ctypes.create_string_buffer(self.head_struct.size)
            self.head_struct.pack_into(b, 0, *values)
            self.sock.send(b)
            print(b.raw)
        except:
            print('Deu merda em send_header')
            raise

    def receive_header(self, sock):
        try:
            data = sock.recv(self.head_struct.size)
            unpacked_data = self.head_struct.unpack(data)

            # Print head in hex
            b = ctypes.create_string_buffer(self.head_struct.size)
            self.head_struct.pack_into(b, 0, *unpacked_data)
            print(binascii.hexlify(b.raw))

        except:
            print('Deu merda em receive_header')
            raise
        return unpacked_data

    def start(self):
        try:
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(5)
        except:
            print('Unable to connect')
            raise
        self.send_header((msg_type.OI, 0, 0, 0))
        data = self.sock.recv(RECV_BUFFER)
        print(data)

        print('Connected to remote host. Start sending messages')

        while True:
            socket_list = [sys.stdin, self.sock]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == self.sock:
                    data = sock.recv(RECV_BUFFER)
                    if not data :
                        print('\nDisconnected from chat server')
                        sys.exit()
                    else :
                        #print data
                        sys.stdout.write(data)
                        self.prompt()

                #user entered a message
                else :
                    msg = sys.stdin.readline()
                    self.send_header((msg_type.MSG, 0, 2**16-1, 0))
                    self.sock.send(msg)
                    self.prompt()

    def prompt(self):
        sys.stdout.write('<Me> ')
        sys.stdout.flush()

def main(args):
    if(len(args) < 3) :
        print('Usage : python client.py <hostname> <port>')
        sys.exit()

    host = args[1]
    port = int(args[2])

    client = Client(host=host, port=port)
    client.start()


if __name__ == "__main__":
    main(sys.argv)
