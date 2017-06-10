#include "message.h"

int main(int argc, char* argv[])
{
	char *ip, *port;
	int socketFD, portNum;
	struct sockaddr_in exibidor_addr;

	ip = strtok(argv[1], ":");
	port = strtok(NULL, " ");

	portNum = atoi(port);
	memset((char*) &exibidor_addr, '\0', sizeof(struct sockaddr));
	exibidor_addr.sin_family = AF_INET;
	exibidor_addr.sin_port = htons(portNum);
	inet_pton(AF_INET, ip, &exibidor_addr.sin_addr);

	printf("Sou o exibidor. Quero conectar ao servidor no endereço %s porta %s\n", ip, port);
	return 0;
}