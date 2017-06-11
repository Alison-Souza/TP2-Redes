from utils import *

class Connection:
    def __init__(self, id, addr, sock, type_client):
        # id of client
        self.id = id
        # set connections
        self.con = []
        # address of client
        self.addr = addr
        # sock module
        self.sock = sock
        # 2^(12)-1 and 2^(13)-1 for exibidor
        # 'ex' 'em'
        self.type = type_client

    def getId(self):
        return self.id

    def getConnections(self):
        return self.con

    def addConnection(self, x):
        if x is list:
            self.con += x
        else:
            self.con.append(x)

    def getAddr(self):
        return self.sock.getsockname()

    def getSock(self):
        return self.sock

    def getType(self):
        return self.type

    def __del__(self):
        # if not close
        # TODO: Send FLW?
        self.sock.close()

class Server:
    def __init__(self, port):
        self.port = port
        # List to keep track of socket descriptors
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(10)
        # Add server socket to the list of readable connections
        self.connections = []
        '''
        Tipo de Mensagem, ID de origem, ID de destino, Numero de sequencia
        '''
        self.head_struct = struct.Struct('! H H H H')

    def __del__(self):
        # TODO: send FLW to everybody
        self.server_socket.close()

    def getSockById(self, id):
        for conn in self.connections:
            if conn.getId() == id:
                return conn
        return None

    def getIdBySock(self, sock):
        for conn in self.connections:
            if sock == conn.getSock():
                return conn.getId()
        return None

    def getAvailableId(self):
        ids = [x.getId() for x in self.connections]
        if ids is None:
            return 1
        else:
            index = 1
            while True:
                if index in ids:
                    index += 1
                else:
                    break
            return index

    # add a new client and check where i have to put inside a car to beat them up
    def new_connection(self):
        sockfd, addr = self.server_socket.accept()
        header = self.receive_header(sockfd)

        id_type = header[0]
        if id_type != msg_type.OI:
            return None

        id_origin = header[1]

        # values for send_back
        ret = [0,0,0,0]

        if id_origin == 0: # is Exhibitor
            id = self.getAvailableId()
            conn = Connection(id, addr, sockfd, 'ex')
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[2] = id
        elif 0 < id_origin < 2**12: # is Emitter
            conn = Connection(id_origin, addr, sockfd, 'em')
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[2] = id_origin
        elif 2**12 <= id_origin < 2**13 - 1:
            # TODO: find the Exhibitor with this id_origin
            sock = self.getSockById(id_origin).getSock()
            ret[0] = msg_type.ERRO

        self.send_header(ret, sockfd)

        return sockfd

    def receive_header(self, sock):
        try:
            data = sock.recv(self.head_struct.size)
            unpacked_data = self.head_struct.unpack(data)

            # Print head in hex
            b = ctypes.create_string_buffer(self.head_struct.size)
            self.head_struct.pack_into(b, 0, *unpacked_data)
            print(bcolors.BOLD + str(binascii.hexlify(b.raw)) + bcolors.ENDC)

        except:
            print(bcolors.FAIL + 'Deu merda em receive_header' + bcolors.ENDC)
            raise
        return unpacked_data

    def receive_data(self, sock):
        try:
            data = sock.recv(RECV_BUFFER - self.head_struct.size)
        except:
            # TODO: check which is correct
            # addr = sock.getpeername()
            addr = sock.getsockname()
            self.broadcast_data(sock, "Client (%s, %s) is offline" % addr)
            print("Client (%s, %s) is offline" % addr)
            sock.close()
            self.connections.remove(sock)
            return None
        return data

    def send_header(self, values, sock):
        if values is not tuple:
            values = tuple(values)
        try:
            b = ctypes.create_string_buffer(self.head_struct.size)
            self.head_struct.pack_into(b, 0, *values)
            sock.send(b)
        except:
            print('Deu merda em send_header')
            raise

    # To the all things
    def start(self):
        print(bcolors.HEADER + "Chat server started on port " + str(self.port) + bcolors.ENDC)

        connections_list = [self.server_socket]

        while True:
            # add input fd for commands purpose
            socket_list = [sys.stdin] + connections_list

            # stuck in here until a fd is ready
            try:
                read_sockets, write_sockets, error_sockets = select.select(socket_list,[],[])
            except Exception as e:
                sys.exit()

            for sock in read_sockets:
                # Add a new connection
                if sock == self.server_socket:
                    # expect type OI message
                    sockfd = self.new_connection()
                    if sockfd is not None:
                        connections_list.append(sockfd)
                # do a command to server
                elif sock == sys.stdin:
                    command = sys.stdin.readline()
                    if command[:-1] == 'help':
                        # TODO: Do a help message
                        pass
                    elif command[:-1] == 'exit':
                        # TODO: send FLW to all clients
                        sys.exit()
                    elif command[:-1] == 'list':
                        # TODO: show a list of connections
                        print(self.connections)

                #Some incoming message from a client
                else:
                    # Data received from client, process it
                    header = self.receive_header(sock)

                    if header[0] == msg_type.OK:
                        # Toda as mensagens tem que ter um OK. O envio de uma mensagem de
                        # OK nao incrementa o numero de sequencia das mensagens do cliente (mensagens de OK nao tem
                        # numero de sequencia proprio
                        pass
                    elif header[0] == msg_type.ERRO:
                        # igual ao OK mas indicando que alguma coisa deu errado
                        pass
                    elif header[0] == msg_type.OI:
                        print(bcolors.FAIL + 'Impossible situation' + bcolors.ENDC)
                        # Tem alguma coisa dando muito errado ai
                    elif header[0] == msg_type.FLW:
                        pass
                    elif header[0] == msg_type.MSG:
                        # receive as string
                        data = self.receive_data(sock)
                        if data:
                            print(bcolors.OKBLUE + data + bcolors.ENDC)
                            # self.broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)
                        else:
                            continue
                    elif header[0] == msg_type.CREQ:
                        pass
                    elif header[0] == msg_type.CLIST:
                        # uma chatice, leia documentacao, no final o cliente responde OK
                        pass


def main():
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 5000
    server = Server(port)
    server.start()

if __name__ == "__main__":
    main()
