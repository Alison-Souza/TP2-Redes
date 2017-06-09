# Exemplo de Makefile básico by Alison Souza
# O símbolo @ antes de um comando evita a impressão do comando.
CC = @gcc
CFLAGS = -g -Wall
PROGRAM_NAME = main
OBJ = tp2.o 
# serv.o exib.o

#all: $(PROGRAM_NAME)
all:
	$(CC) -c $(CFLAGS) tp2.c
#	$(CC) -c $(CFLAGS) serv.c
	$(CC) $(CFLAGS) $(OBJ) -o $(PROGRAM_NAME)

run:
	@./main

clean:
	@rm -rf *.o *.a *.out
	@rm main 2>/dev/null || true
# O (2>/dev/null || true) evita mensagens de erro caso não exista main.
