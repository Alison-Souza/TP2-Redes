# Exemplo de Makefile básico by Alison Souza
# O símbolo @ antes de um comando evita a impressão do comando.
CC = @gcc
CFLAGS = -g -Wall
PROGRAM_NAME1 = serv
PROGRAM_NAME2 = emissor
PROGRAM_NAME3 = exibidor
OBJ1 = serv.o
OBJ2 = emissor.o
OBJ3 = exibidor.o
PORT = 55000

all:
	$(CC) -c $(CFLAGS) serv.c
	$(CC) -c $(CFLAGS) emissor.c
	$(CC) -c $(CFLAGS) exibidor.c
	$(CC) $(CFLAGS) $(OBJ1) -o $(PROGRAM_NAME1)
	$(CC) $(CFLAGS) $(OBJ2) -o $(PROGRAM_NAME2)
	$(CC) $(CFLAGS) $(OBJ3) -o $(PROGRAM_NAME3)

run:
	@./serv $(PORT)
	@./emissor
	@./exibidor

clean:
	@rm -rf *.o *.a *.out
	@rm serv 2>/dev/null || true
	@rm emissor 2>/dev/null || true
	@rm exibidor 2>/dev/null || true
	@clear
# O (2>/dev/null || true) evita mensagens de erro caso não exista main.
