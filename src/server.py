#!/usr/bin/python3

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

    # Retorna todas as conexoes do servidor,
    # contem uma lista de emissores e exibidores
    def getConnections(self):
        return self.con

    # Store of ids to exhibitors
    # Adiciona emissor ou exibidor na lista
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
        print_error('Connection died!')

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

        # dict to store who can send message to who
        self.graph = dict()

    def __del__(self):
        print_blue('Sendind FLW to all clients!')
        for conn in self.connections:
            id_to_close = conn.getId()
            try:
                self.send_data((msg_type.FLW, SERVER_ID, id_to_close, 0), conn.sock)
            except:
                print_error('Error trying to send data from ' + str(id_to_close))
            try:
                # TODO: Don't know how to fix this
                data = conn.sock.receive_data()
                head, id_origin, id_destiny, seq_num = self.extract_header(data)
                if head == msg_type.OK and id_origin == id_to_close:
                    print_blue('Closing connection with ' + str(id_origin))
                    conn.sock.close()
                else:
                    # TODO: Try again?
                    pass
            except:
                print_error('Error trying to receive data from ' + str(id_to_close))

        print_error('SPOILERS: Darth Vader died!')
        self.server_socket.close()

    # Retorna o socket do cliente passando o id como parametro
    def getSockById(self, id):
        for conn in self.connections:
            if conn.getId() == id:
                return conn.getSock()
        return None

    # Retorna o socket do cliente passando pelo ID
    def getIdBySock(self, sock):
        for conn in self.connections:
            if sock == conn.getSock():
                return conn.getId()
        return None

    # Remove o cliente da lista passando o id ou socket
    def removeSock(self, param):
        # param can be Id or sock object

        if param is int:
            for conn in self.connections:
                if param == conn.getId():
                    print_warning('Remove:', end=" ")
                    print_warning(conn.getId())
                    self.connections.remove(conn)
                    return True
        else: # sock object
            for conn in self.connections:
                if param == conn.getSock():
                    print_warning('Remove:', end=" ")
                    print_warning(conn.getId())
                    self.connections.remove(conn)
                    return True
        print_warning('Cannot find sock to remove:')
        print_warning(param)
        return False

    # Pega o primeiro id disoiivel passando um id inicial com parametro
    def getAvailableId(self, init_value=2**12):
        ids = [x.getId() for x in self.connections]
        if ids is None:
            return init_value
        else:
            index = init_value
            while True:
                if index in ids:
                    index += 1
                else:
                    break
            return index

    # Metodo que configura uma nova conexao de um cliente
    # Verifica se eh um exibidor ou emissor e associa um id
    def new_connection(self):
        sockfd, addr = self.server_socket.accept()
        data = self.receive_data(sockfd)
        header = self.extract_header(data)

        id_type = header[0]
        if id_type != msg_type.OI:
            return None

        id_origin = header[1]

        # values for send_back
        ret = [0,0,0,0]

        if id_origin == 0: # is Exhibitor
            print_blue('New Exhibitor tring to connect')
            id = self.getAvailableId(2**12)
            conn = Connection(id, addr, sockfd, 'ex')
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[1] = SERVER_ID
            ret[2] = id
        elif 0 < id_origin < 2**12: # is Emitter
            # Useless because don't associate a Exhibitor
            print_blue('New Emitter tring to connect')
            conn = Connection(id_origin, addr, sockfd, 'em')
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[2] = id_origin
        elif 2**12 <= id_origin < 2**13 - 1: # is Emitter
            print_blue('New Emitter tring to connect')
            sock = self.getSockById(id_origin)
            if sock is not None:
                ret[0] = msg_type.OK
                ret[1] = SERVER_ID
                ret[2] = self.getAvailableId(1)
                conn = Connection(ret[2], addr, sockfd, 'em')
                self.connections.append(conn)
                conn.addConnection(id_origin)
                message = '**** User ' +str(ret[2]) + ' connected to chat\n'
                self.send_data((msg_type.MSG, SERVER_ID, self.getIdBySock(sock), 0), sock, message)
            else:
                ret[0] = msg_type.ERRO
                ret[1] = SERVER_ID

        self.send_data(ret, sockfd)
        return sockfd

    # Extrai e retorna o cabecalho do buffer data
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

    # Recebe e retorna o dado do socket
    def receive_data(self, sock):
        try:
            data = sock.recv(RECV_BUFFER)
        except:
            # TODO: check which is correct
            # addr = sock.getpeername()
            addr = sock.getsockname()
            # self.broadcast_data(sock, "Client (%s, %s) is offline" % addr)
            print("Client (%s, %s) is offline" % addr)
            sock.close()
            # TODO: Remove from connected clients
            self.connections.remove(sock)
            return None
        return data

    # Constroi o cabecalho concatenado a mensagem em formato binario
    def send_data(self, header, sock, data=''):
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
            sock.send(b)
        except:
            print_error('Deu shit em send_data')
            raise

    # To the all things
    def start(self):
        print_header("Chat server started on port " + str(self.port))

        connections_list = [self.server_socket]

        while True:
            # add input fd for commands purpose
            socket_list = [sys.stdin] + connections_list

            # stuck in here until a fd is ready
            try:
                read_sockets, write_sockets, error_sockets = select.select(socket_list,[],[])
            except Exception as e:
                print_error('Something wrong in select')
                print_error(socket_list)
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
                    if command[:-1] == '/help':
                        print_green('Server Chat:\nUse one of commands below')
                        print_green('  /status\t-- Show ids and connections in active')
                        print_green('  /quit\t-- Exit')
                        print_green('  /list\t-- print all connections')
                    elif command[:-1] == '/status':
                        for conn in self.connections:
                            print_green(str(conn.getId()) + str(conn.getConnections()))
                    elif command[:-1] == '/quit':
                        sys.exit()
                    elif command[:-1] == '/list':
                        # TODO: show a list of connections
                        print_green(self.connections)

                #Some incoming message from a client
                else:
                    # Data received from client, process it
                    data = self.receive_data(sock)
                    print_bold(data)

                    header = self.extract_header(data)
                    # Remove socket if send nothing
                    if header is None:
                        print_warning('header is None, why?')
                        aux_id = self.getIdBySock(sock)
                        self.removeSock(sock)
                        connections_list.remove(sock)
                        continue
                    else:
                        head, id_origin, id_destiny, seq_num = header[:4]

                    if head == msg_type.OK:
                        # Toda as mensagens tem que ter um OK. O envio de uma mensagem de
                        # OK nao incrementa o numero de sequencia das mensagens do cliente (mensagens de OK nao tem
                        # numero de sequencia proprio
                        pass
                    elif head == msg_type.ERRO:
                        # igual ao OK mas indicando que alguma coisa deu errado
                        print_error(str(sock.getpeername()) + ' ' + data, end="")
                    elif head == msg_type.OI:
                        print_error('Impossible situation!\nPray for modern gods of internet!')
                    elif head == msg_type.FLW:
                        print_warning('send FLW for everyone')
                        # TODO: send FLW to everyone and wait OK
                    elif head == msg_type.MSG:
                        # Receive message
                        data = data[self.head_struct.size:].decode('ascii')
                        # TODO: while true for read more messages?
                        if data:
                            print_blue(str(sock.getpeername()) + ' ' + data, end="") # DEBUG purpose
                            for conn in self.connections:
                                if conn == self.server_socket:
                                    continue
                                if conn.getId() == id_origin:
                                    for who_to_send in conn.getConnections():
                                        print_blue('Trying to send message from ' + str(id_origin) + ' to ' + str(who_to_send))
                                        self.send_data((msg_type.MSG, id_origin, who_to_send, 0), self.getSockById(who_to_send), data)
                                        # TODO: wait OK?
                                    break
                        else:
                            continue
                    elif head == msg_type.CREQ:
                        pass
                    elif head == msg_type.CLIST:
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
