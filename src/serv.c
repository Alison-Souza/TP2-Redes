#include "message.h"

int main(int argc, char* argv[])
{
	int socketFD, portNum;
	struct sockaddr_in server_addr;

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

	printf("Sou o servidor na porta %d\n", portNum);
	return 0;
}