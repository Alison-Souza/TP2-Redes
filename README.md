# TP2-Redes
Trabalho Prático 2 da disciplina de Redes: Sistema de Mensagens Orientado a Eventos

* Objetivos:
Definir formato das mensagens e protocolo.
Implementar utilizando sockets, centrado ao redor da função 'select'.

* Mensagens devem ter cabeçalho com:
Tipo da mensagem.
Identificador de origem.
Identificador de destino.
Número de sequência.

* Mensagens podem ser dos tipos:
- OK: confirmação que mensagem foi enviada corretamente.
- ERRO: espécie de confirmação, que indica algum erro.
- OI: mensagem de conexão e identificação de um cliente a um servidor.
- FLW: mensagem para desconectar um cliente do servidor. 
- MSG: mensagem propriamente dita, de um cliente para outro através do servidor.
- CREQ: mensagem de requisição da lista de clientes, pedida por um cliente.
- CLIST: parte da resposta de um servidor a mensagem CREQ. (OK também)

* Identificadores:
- Emissores: entre 1 e (2¹² - 1)
- Exibidores: entre 2¹² e (2¹³ - 1)
- Servidor: (2^16 - 1)

* Um emissor não necessariamente deve estar associado a um exibidor, e vice versa. 

* Protocolo TCP. No servidor, um socket deve ser mantido para receber novas conexões (onde haverá accept) e ter um socket para cada cliente distinto.

* O servidor deve ser iniciado recebendo como parâmetro apenas o número do porto onde ele deve ouvir por conexões dos clientes.

* Um emissor deve ser disparado com um parâmetro obrigatório que identifica a localização do servidor como um par “endereço IP:porto”.

* Um exibidor deve ser disparado com um parâmetro obrigatório que identifica a localização do servidor como um par “endereço IP:porto”, que pode ser seguido por um segundo parâmetro, opcional, com o identificador de um emissor, caso uma associação deva ser feita.

