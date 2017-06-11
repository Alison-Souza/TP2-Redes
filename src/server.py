# From Python 2.6 you can import the print function from Python 3:
from __future__ import print_function
import socket
import select
import sys

import struct
import binascii
import ctypes

# keep it as an exponent of 2
RECV_BUFFER = 4096

class Connection:
    def __init__(self, id, addr, sock):
        self.id = id
        self.addr = addr
        self.sock = sock

    def getId(self):
        return self.id

    def getaddr(self):
        return self.sock.getsockname()

    def getSock(self):
        return self.sock

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
        self.connections.append(self.server_socket)
        self.head_struct = struct.Struct('! H H H H')

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

    # Function to broadcast chat messages to all connected clients
    def broadcast_data (self, sock, message):
        # Do not send the message to master socket and the client who has send us the message
        for socket in self.connections:
            if socket != self.server_socket and socket != sock :
                try :
                    socket.send(message)
                except :
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    socket.close()
                    self.connections.remove(socket)

    def start(self):
        print("Chat server started on port " + str(self.port))

        while True:
            # add input fd for commands purpose
            socket_list = [sys.stdin] + self.connections
            # Get the list sockets which are ready to be read through select
            try:
                read_sockets, write_sockets, error_sockets = select.select(socket_list,[],[])
            except Exception as e:
                sys.exit()

            for sock in read_sockets:
                #New connection
                if sock == self.server_socket:
                    # Handle the case in which there is a new connection recieved through self.server_socket
                    sockfd, addr = self.server_socket.accept()
                    self.connections.append(sockfd)
                    print("Client (%s, %s) connected" % addr)

                    self.broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)

                # do a command from server
                elif sock == sys.stdin:
                    command = sys.stdin.readline()
                    if command[:-1] == 'exit':
                        # TODO: send FLW to all clients
                        sys.exit()
                    elif command[:-1] == 'list':
                        # TODO: show a list of connections
                        print(self.connections)

                #Some incoming message from a client
                else:
                    # Data received from client, process it
                    header = self.receive_header(sock)
                    # receive as string
                    data = self.receive_data(sock)
                    if data:
                        self.broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)
                    else:
                        continue

        self.server_socket.close()

def main():
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 5000
    server = Server(port)
    server.start()

if __name__ == "__main__":
    main()
