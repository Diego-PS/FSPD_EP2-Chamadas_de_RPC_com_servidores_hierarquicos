from concurrent import futures # usado na definição do pool de threads

import grpc

import threading

import integracao_pb2, integracao_pb2_grpc # módulos gerados pelo compilador de gRPC

import sys

import socket
import math

porto : int = sys.argv[1]

# Interface para o conteúdo a ser armazenado, 
# contendo uma descrição (desc) e um valor (valor)
class Servidor:
   def __init__(self, nome: str, porto: int):
      self.nome = nome
      self.porto = porto

# Armazena os objetos inseridos, 
# trata-se de um dicionário que mapeira uma chave a um 
servidores : dict[int, Servidor] = {}

# Os procedimentos oferecidos aos clientes precisam ser encapsulados
#   em uma classe que herda do código do stub.
class DoStuff(integracao_pb2_grpc.DoStuffServicer):
   
   # Adiciona o método stop_envent no construtor, para terminar a execução do servidor
   def __init__(self, stop_event):
      self._stop_event = stop_event
   
   # registro: recebe como parâmetros o nome da máquina onde um 
   # servidor de diretórios independente está executando e um
   # inteiro indicando o número do porto usado por ele, 
   # seguidos por uma lista com todas as chaves contidas naquele servidor (inteiros). 
   # Deve retornar o número de chaves recebidas ou zero, 
   # se seu código detectar algum erro (normalmente não seria necessário);
   def registro(self, request, context):
      nome_dir = request.nome
      porto_dir = request.porto
      servidor = Servidor(nome_dir, porto_dir)
      chaves = request.chaves
      try:
         for chave in chaves:
            servidores[chave] = servidor
         return integracao_pb2.RespostaRegistro(num=len(chaves))
      except:
         return integracao_pb2.RespostaRegistro(num=0)
      

   # consulta: recebe como parâmetro o inteiro positivo ch e 
   # consulta um diretório local para ver se conhece a chave indicada. 
   # Em caso afirmativo, retorna um string indicando o nome (ou endereço IP) 
   # do participante que contém aquela chave e um inteiro indicando 
   # o número do porto a ser usado para contactá-lo. Em caso negativo, 
   # retorna o string "ND" e um inteiro qualquer (p.ex., zero);
   def consulta(self, request, context):
      chave = request.chave
      if chave in servidores:
         serv = servidores[chave]
         return integracao_pb2.RespostaConsulta(nome=serv.nome, porto=serv.porto)
      else:
         return integracao_pb2.RespostaConsulta(nome='ND', porto=0)
      
   # término: um procedimento sem parâmetros que indica que o 
   # servidor deve terminar sua execução; nesse caso o servidor deve responder 
   # com um inteiro igual ao número de chaves registradas até então e 
   # terminar sua execução depois da resposta.
   def termino(self, request, context):
      self._stop_event.set()
      return integracao_pb2.RespostaTermino(num=len(servidores))

def serve():
   # Evento para encerrar a execução do servidor
   stop_event = threading.Event()
   # O servidor usa um modelo de pool de threads do pacote concurrent
   server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
   # O servidor precisa ser ligado ao objeto que identifica os
   #   procedimentos a serem executados.
   integracao_pb2_grpc.add_DoStuffServicer_to_server(DoStuff(stop_event), server)
   # O método add_insecure_port permite a conexão direta por TCP
   #   Outros recursos estão disponíveis, como uso de um registry
   #   (dicionário de serviços), criptografia e autenticação.
   server.add_insecure_port(f'{socket.getfqdn()}:{porto}')
   # O servidor é iniciado e esse código não tem nada para fazer
   #   a não ser esperar pelo término da execução.
   server.start()
   # Espera até terminar
   stop_event.wait()
   # Termina
   server.stop(None)

if __name__ == '__main__':
    serve()
