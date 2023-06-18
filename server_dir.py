from concurrent import futures # usado na definição do pool de threads

import grpc

import threading

import diretorios_pb2, diretorios_pb2_grpc, integracao_pb2, integracao_pb2_grpc # módulos gerados pelo compilador de gRPC

import sys

import socket

nome : str = socket.getfqdn()
porto : int = int(sys.argv[1])

# Interface para o conteúdo a ser armazenado, contendo uma descrição (desc) e um valor (valor)
class Conteudo:
   def __init__(self, desc: str, valor: float):
      self.desc = desc
      self.valor = valor

# Armazena os objetos inseridos, trata-se de um dicionário que mapeira uma chave a um 
diretorios : dict[int, Conteudo] = {}

# Os procedimentos oferecidos aos clientes precisam ser encapsulados
#   em uma classe que herda do código do stub.
class DoStuff(diretorios_pb2_grpc.DoStuffServicer):
   
   # Adiciona o método stop_envent no construtor, para terminar a execução do servidor
   def __init__(self, stop_event):
      self._stop_event = stop_event
   
   # inserção: recebe como parâmetros um inteiro positivo (chave), um string (desc) e um número de ponto flutuante (valor) e armazena desc e valor em um dicionário, associados à chave, caso ela ainda não exista, retorna zero; caso a chave já existia o conteúdo (desc e valor) devem ser atualizados e o valor 1 deve ser retornado;
   def insercao(self, request, context):
      chave = request.chave
      desc = request.desc
      valor = request.valor
      if chave in diretorios:
         diretorios[chave] = Conteudo(desc, valor)
         return diretorios_pb2.RespostaInsercao(resposta=1)
      else:
         diretorios[chave] = Conteudo(desc, valor)
         return diretorios_pb2.RespostaInsercao(resposta=0)
      
   # consulta: recebe como parâmetros um inteiro positivo (chave) e retorna o conteúdo do string e valor associados à chave, caso ela exista, ou um string nulo e o valor zero caso contrário;
   def consulta(self, request, context):
      chave = request.chave
      if chave in diretorios:
         dir = diretorios[chave]
         return diretorios_pb2.RespostaConsulta(desc=dir.desc, valor=dir.valor)
      else:
         return diretorios_pb2.RespostaConsulta(desc='', valor=0)
      
   # registro: recebe como parâmetro um string com o nome de uma máquina e um inteiro identificando um porto naquela máquina. Esse comando só faz sentido para utilizar o serviço que será definido na segunda parte. Ao ser executado, o servidor deve se conectar como cliente de um servido de integração localizado na máquina/porto passados como parâmetros e disparar o procedimento de registro daquele servidor (descrito na segunda parte); ao final, deve retornar para o cliente o valor retornado pelo outro servidor;
   def registro(self, request, context):
      nome_int: str = request.nome
      porto_int: int = request.porto
      # Primeiro, é preciso abrir um canal para o servidor
      channel = grpc.insecure_channel(f'{nome_int}:{porto_int}')
      # E criar o stub, que vai ser o objeto com referências para os
      # procedimentos remotos (código gerado pelo compilador)
      stub = integracao_pb2_grpc.DoStuffStub(channel)
      resposta = stub.registro(integracao_pb2.RequisicaoRegistro(nome=nome, porto=porto, chaves=[chave for chave in diretorios]))
      return diretorios_pb2.RespostaTermino(num=resposta.num)
      
   # término: um procedimento sem parâmetros que indica que o servidor deve terminar sua execução; nesse caso o servidor deve responder com um inteiro igual ao número de chaves armazenadas até então e terminar sua execução depois da resposta.
   def termino(self, request, context):
      self._stop_event.set()
      return diretorios_pb2.RespostaTermino(num=len(diretorios))

def serve():
   # Evento para encerrar a execução do servidor
   stop_event = threading.Event()
   # O servidor usa um modelo de pool de threads do pacote concurrent
   server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
   # O servidor precisa ser ligado ao objeto que identifica os
   #   procedimentos a serem executados.
   diretorios_pb2_grpc.add_DoStuffServicer_to_server(DoStuff(stop_event), server)
   # O método add_insecure_port permite a conexão direta por TCP
   #   Outros recursos estão disponíveis, como uso de um registry
   #   (dicionário de serviços), criptografia e autenticação.
   server.add_insecure_port(f'{nome}:{porto}')
   # O servidor é iniciado e esse código não tem nada para fazer
   #   a não ser esperar pelo término da execução.
   server.start()
   # Espera até terminar
   stop_event.wait()
   # Termina
   server.stop(None)

if __name__ == '__main__':
    serve()
