#!/usr/bin/python3

from utils import *

class Connection:
    def __init__(self, id, addr, sock, tclient):
        # id of client
        self.id = id
        # set connections
        self.con = None
        # address of client
        self.addr = addr
        # sock module
        self.sock = sock
        # 2^(12)-1 and 2^(13)-1 for exibidor
        # client_type.EMISSOR or client_type.EXIBIDOR
        self.type = tclient

    def get_id(self):
        return self.id

    # Retorna todas as conexoes do servidor,
    # contem uma lista de emissores e exibidores
    def get_connection(self):
        return self.con

    # Store of ids to exhibitors
    # Adiciona emissor ou exibidor
    def set_connection(self, x):
        if x is not int:
            print_error('Int expected but received ' + str(x))
        self.con = x

    def get_addr(self):
        return self.sock.getsockname()

    def get_sock(self):
        return self.sock

    def get_type(self):
        return self.type

    def __del__(self):
        # if not close
        self.sock.close()
        print_error('Connection died!')

class Server:
    def __init__(self, port):
        self.port = port
        # List to keep track of socket descriptors
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen()
        # Add server socket to the list of readable connections
        # Store only class Connection
        self.connections = []
        # Tipo de Mensagem, ID de origem, ID de destino, Numero de sequencia

    def __del__(self):
        print_blue('Sendind FLW to all clients!')
        # TODO: Send FLW e espera o OK
        self.server_socket.close()

    # Retorna o socket do cliente passando o id como parametro
    def get_sock_by_id(self, id):
        for conn in self.connections:
            if conn.get_id() == id:
                return conn.get_sock()
        print_error('Cannot get sock by id ' + str(id))
        return None

    # Retorna o socket do cliente passando pelo ID
    def get_id_by_sock(self, sock):
        for conn in self.connections:
            if conn.get_sock() == sock:
                return conn.get_id()
        print_error('Cannot get id by sock\n' + str(id))
        return None

    # Remove o cliente da lista passando o id ou socket
    def remove_sock(self, param):
        # param can be Id or sock object

        if param is int: # it's ID
            for conn in self.connections:
                if param == conn.get_id():
                    print_warning('Remove:', end=" ")
                    print_warning(conn.get_id())
                    self.connections.remove(conn)
                    return True
        else: # it's a sock object
            for conn in self.connections:
                if param == conn.getSock():
                    print_warning('Remove:', end=" ")
                    print_warning(conn.get_id())
                    self.connections.remove(conn)
                    return True
        print_error('Cannot find sock to remove:')
        print_error(param)
        return False

    # Pega o primeiro id disponivel passando um id inicial como parametro
    def get_available_id(self, init_value=2**12):
        ids = [x.get_id() for x in self.connections]
        if ids is None:
            return init_value
        else:
            index = init_value
            while True:
                if index == SERVER_ID:
                    print_error('Full connections')
                    return None
                if index in ids:
                    index += 1
                else:
                    break
            return index

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

    # Constroi o cabecalho concatenado a mensagem em formato binario e envia pelo socket
    def send_data(self, sock, header, data=''):
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
            sock.send(b)
        except:
            print_error('Erro in trying to send data')
            return False
        return True

    def receive_data(self, sock, size):
        print_warning('receive_data')
        try:
            data = sock.recv(size)
            print_bold(data)
            if not data :
                print_error('\nDisconnected from chat server')
                sys.exit()
        except:
            print_error('Error in receive data!')
            return None
            # sys.exit()
        return data

    def receive_header(self, sock):
        data = self.receive_data(sock, Header.struct.size)
        return Header.struct.unpack(data)

    # Metodo que configura uma nova conexao de um cliente
    # Verifica se eh um exibidor ou emissor e associa um id
    def new_connection(self):
        print_warning('new_connection')
        new_sock, addr = self.server_socket.accept()
        header = self.receive_header(new_sock)

        id_type = header[0]
        if id_type != msg_type.OI:
            print_error('Expected OI MSG, but receive type: ' + str(id_type))
            return None

        id_origin = header[1]

        # values for send_back to client
        ret = [0,0,0,0]

        if id_origin == 0: # is Exhibitor
            print_blue('New Exhibitor tring to connect')
            id = self.get_available_id(2**12)
            conn = Connection(id, addr, new_sock, client_type.EXIBIDOR)
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[1] = SERVER_ID
            ret[2] = id
        elif 0 < id_origin < 2**12: # is Emitter
            # Useless because don't associate a Exhibitor
            print_blue('New Emitter tring to connect')
            conn = Connection(id_origin, addr, new_sock, client_type.EMISSOR)
            self.connections.append(conn)
            ret[0] = msg_type.OK
            ret[2] = id_origin
        elif 2**12 <= id_origin < 2**13 - 1: # is Emitter
            print_blue('New Emitter tring to connect')
            sock = self.get_sock_by_id(id_origin)
            if sock is not None:
                ret[0] = msg_type.OK
                ret[1] = SERVER_ID
                ret[2] = self.get_available_id(1)
                conn = Connection(ret[2], addr, new_sock, client_type.EMISSOR)
                self.connections.append(conn)
                conn.set_connection(id_origin)
                # TODO: Esta mensagem tem que ser mandada por broadcast
                # message = '**** User ' + str(ret[2]) + ' connected to chat\n'
                # self.send_data(sock, (msg_type.MSG, SERVER_ID, self.get_id_by_sock(sock), 0), message)
            else:
                ret[0] = msg_type.ERRO
                ret[1] = SERVER_ID
                # TODO: Consertar isso depois
                raise

        self.send_data(new_sock, ret)
        print_warning('DONE new_connection')
        return new_sock

    # Recebe comandos do teclado para sair, listar conexões, etc.
    def get_command_from_stdin(self):
        command = sys.stdin.readline()
        if command[:-1] == '/help':
            print_green('Server Chat:\nUse one of commands below')
            print_green('  /status\t-- Show ids and connections in active')
            print_green('  /quit\t-- Exit')
            print_green('  /list\t-- print all connections')
        elif command[:-1] == '/status':
            if self.connections == []:
                print_green('No connections')
            for conn in self.connections:
                print_green(str(conn.get_id()) + ' --> ' + str(conn.get_connection()))
        elif command[:-1] == '/quit':
            sys.exit()
        elif command[:-1] == '/list':
            # TODO: Melhorar isso
            print_green(self.connections)

    # Recebe os dados do socket e repassa a responsabilidade pra outro metodo
    def get_data_from_sock(self, sock):
        header = self.receive_header(sock)
        # Remove socket if send nothing
        if header is None or len(header) < 4:
            print_error('header is None, why?')
            aux_id = self.get_id_by_sock(sock)
            print_error('id:' + str(aux_id))
            self.removeSock(sock)
            connections_list.remove(sock)
            return
        else:
            head, id_origin, id_destiny, seq_num = header[:4]

        if head == msg_type.OK:
            # Toda as mensagens tem que ter um OK. O envio de uma mensagem de
            # OK nao incrementa o numero de sequencia das mensagens do cliente (mensagens de OK nao tem
            # numero de sequencia proprio
            self.handle_ok()
        elif head == msg_type.ERRO:
            # igual ao OK mas indicando que alguma coisa deu errado
            self.handle_erro(sock)
        elif head == msg_type.FLW:
            self.handle_flw(sock)
        elif head == msg_type.MSG:
            self.handle_msg(sock)
        elif head == msg_type.CREQ:
            pass
        elif head == msg_type.CLIST:
            # uma chatice, leia documentacao, no final o cliente responde OK
            pass
        else:
            print_error('Impossible situation!\nPray for modern gods of internet!')
            print_error('Type: ' + str(what_type))
            return

    def handle_ok(self):
        print_warning('Receive OK from: ' + str(id_origin))
        print_warning('Seq number: ' + str(seq_num))

    def handle_erro(self, sock):
        print_error(str(sock.getpeername()) + ' ' + data, end="")
        # TODO: Esse erro tem que tratar todos os casos
        # erro no OI, MSG, etc

    def handle_flw(self, sock):
        print_blue('Send OK from FLW back to client')
        self.send_data(sock, (msg_type.OK, SERVER_ID, self.get_sock_by_id(sock), 0))
        time.sleep(5)
        self.remove_sock(sock)

    def handle_msg(self, sock):
        print_error('MSG received from '+ str(id_origin) + ', it\'s not for me!')
        # Receive message
        data = data[self.head_struct.size:].decode('ascii')
        # TODO: while true for read more messages?
        if data:
            print_blue(str(sock.getpeername()) + ' ' + data, end="") # DEBUG purpose
            for conn in self.connections:
                if conn == self.server_socket:
                    continue
                if conn.get_id() == id_origin:
                    for who_to_send in conn.getConnections():
                        print_blue('Trying to send message from ' + str(id_origin) + ' to ' + str(who_to_send))
                        self.send_data((msg_type.MSG, id_origin, who_to_send, 0), self.get_sock_by_id(who_to_send), data)
                        # TODO: wait OK?
                    break
        else:
            return

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

    # To the all things
    def start(self):
        print_header("Chat server started on port " + str(self.port))
        print_header('It\'s dangerous to go outise,')
        print_header('type \'/help\' for more.')

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
                    new_sock = self.new_connection()
                    if new_sock is not None:
                        connections_list.append(new_sock)
                # do a command to server
                elif sock == sys.stdin:
                    self.get_command_from_stdin()
                # Something incoming message from a client
                else:
                    self.get_data_from_sock(sock)

def main():
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 5000
    server = Server(port)
    server.start()

if __name__ == "__main__":
    main()
