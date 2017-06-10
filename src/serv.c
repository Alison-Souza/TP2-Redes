#include "message.h"

int main(int argc, char* argv[])
{
	int socketFD, portNum, i;
	struct sockaddr_in server_addr, new_addr;
	fd_set readSet;

	// Cria um socket.
	socketFD = socket(AF_INET, SOCK_STREAM, 0);
	if(socketFD < 0)
	{
		fprintf(stderr, "ERROR opening socket\n");
		exit(1);
	}
	
	// Define e atribui os dados do socket.
	portNum = atoi(argv[1]);
	memset((char*) &server_addr, '\0', sizeof(server_addr));
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(portNum);
	server_addr.sin_addr.s_addr = INADDR_ANY;

	// Inicia abertura passiva.
	if(bind(socketFD, (struct sockaddr *) &server_addr, sizeof(struct sockaddr)) < 0)
	{
		fprintf(stderr, "ERROR on binding.\n");
		exit(1);
	}

	if(listen(socketFD, 1) < 0)
	{
		fprintf(stderr, "ERROR on listen port.\n");
		exit(1);
	}

	// REALIZA O SELECT ANTES DO LOOP DE ACCEPT
	// https://www.gnu.org/software/libc/manual/html_node/Server-Example.html
	// http://developerweb.net/viewtopic.php?id=2933
	// http://man7.org/linux/man-pages/man2/select.2.html

	// Inicializa o conjunto de sockets.
	FD_ZERO(&readSet);
	FD_SET(socketFD, &readSet);

	// Loop sem condição de terminação. Podemos tentar um modo de terminar
	// o servidor de maneira mais bem comportada.
	while(1)
	{
		// Select permite monitorar vários FD's, verificando se 
		// eles estão prontos para uma leitura/escrita.
		if(select(FD_SETSIZE, &readSet, NULL, NULL, NULL) < 0)
		{
			fprintf(stderr, "ERROR on select.\n");
			exit(1);
		}

		// Percorre toda a lista possível de sockets. 
		// Acho que podemos fazer algo mais eficiente aqui.
		for(i = 0; i < FD_SETSIZE; i++)
		{
			// Se o socket está no conjunto de FD's setado pelo select.
			if(FD_ISSET(i, &readSet))
			{
				// Se o socket a ser usado é o socket do servidor,
				// cria um novo socket para essa conexão.
				if(i == socketFD)
				{
					int newSockFD;
					socklen_t sockSize = sizeof(struct sockaddr_in);
					newSockFD = accept(socketFD, (struct sockaddr *) &new_addr, &sockSize);
					if(newSockFD <  0)
					{
						fprintf(stderr, "ERROR on accept connection.\n");
						exit(1);
					}

					printf("Server: connect from host %s, port %hd.\n", inet_ntoa(new_addr.sin_addr), ntohs(new_addr.sin_port));
					FD_SET(newSockFD, &readSet);
				}
				else // Socket usado já está conectado ao servidor.
				{
					// DO THING
				}
			}
		}
	}


	printf("Sou o servidor na porta %d\n", portNum);
	return 0;
}