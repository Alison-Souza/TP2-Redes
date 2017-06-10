#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define MAXDATASIZE 512
#define OK 1
#define ERRO 2
#define OI 3
#define FLW 4
#define MSG 5
#define CREQ 6
#define CLIST 7

typedef struct message
{
	uint16_t type;
	uint16_t id_source;
	uint16_t id_dest;
	uint16_t seq_num;
	uint16_t num_caracteres; // usado por MSG.
	uint16_t num_clientes; // usado por CLIST.
	uint8_t data[MAXDATASIZE]; // cria um ponteiro apenas e usa malloc ???
} message_t;

/*

Se der tempo, podemos criar uma estrutura de nomes e IDs, para identificar
os usuários do mensageiro. Vale uns pontos extras... haha.
Algo como:

typedef struct client
{
	uint16_t id;
	char nome[MAXNAMESIZE];
} client_t;

*/
