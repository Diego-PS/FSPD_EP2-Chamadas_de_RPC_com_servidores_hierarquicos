from __future__ import print_function # usado internamente nos stubs

import grpc

import integracao_pb2, integracao_pb2_grpc, diretorios_pb2, diretorios_pb2_grpc # módulos gerados pelo compilador de gRPC

import sys

[nome, porto] = sys.argv[1].split(':')

def run():
    # Primeiro, é preciso abrir um canal para o servidor
    channel = grpc.insecure_channel(f'{nome}:{porto}')
    # E criar o stub, que vai ser o objeto com referências para os
    # procedimentos remotos (código gerado pelo compilador)
    stub = integracao_pb2_grpc.DoStuffStub(channel)

    while True:
        entrada = input().split(',')
        comando = entrada[0]
        
        # C,ch - consulta o servidor de integração pela chave ch, que deve responder com o identificador de um servidor de diretório independente. Se a resposta for "ND", esse string deve ser escrito na saída. Caso contrário, o cliente em seguida executa uma consulta àquele servidor indentificado na resposta e escreve na saída o valor de retorno.
        if comando == 'C':
            chave = int(entrada[1])
            resposta = stub.consulta(integracao_pb2.RequisicaoConsulta(chave=chave))
            if resposta.nome == 'ND':
                print('ND')
            else:
                nome_dir = resposta.nome
                porto_dir = resposta.porto
                # Primeiro, é preciso abrir um canal para o servidor
                channel = grpc.insecure_channel(f'{nome_dir}:{porto_dir}')
                # E criar o stub, que vai ser o objeto com referências para os
                # procedimentos remotos (código gerado pelo compilador)
                stub_dir = diretorios_pb2_grpc.DoStuffStub(channel)
                resposta_dir = stub_dir.consulta(diretorios_pb2.RequisicaoConsulta(chave=chave))
                print(f'{resposta_dir.desc},{resposta_dir.valor:7.4f}')

        # T - sinaliza a terminação do servidor, escreve o valor de retorno e termina o cliente.
        if comando == 'T':
            resposta = stub.termino(diretorios_pb2.RequisicaoTermino())
            print(resposta.num)
            channel.close()

if __name__ == '__main__':
    run()
