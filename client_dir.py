from __future__ import print_function # usado internamente nos stubs

import grpc

import diretorios_pb2, diretorios_pb2_grpc # módulos gerados pelo compilador de gRPC

import sys

[nome, porto] = sys.argv[1].split(':')

def run():
    # Primeiro, é preciso abrir um canal para o servidor
    channel = grpc.insecure_channel(f'{nome}:{porto}')
    # E criar o stub, que vai ser o objeto com referências para os
    # procedimentos remotos (código gerado pelo compilador)
    stub = diretorios_pb2_grpc.DoStuffStub(channel)

    while True:
        entrada = input().split(',')
        comando = entrada[0]
        
        # I,ch,um string de descrição,val - insere no servidor a chave ch, 
        # associada ao string e ao valor val, 
        # escreve na saída padrão o valor de retorno do procedimento (0 ou 1);
        if comando == 'I':
            chave = int(entrada[1])
            desc = entrada[2]
            valor = float(entrada[3])
            resposta = stub.insercao(diretorios_pb2.RequisicaoInsercao(chave=chave, desc=desc, valor=valor))
            print(resposta.resposta)
        
        # C,ch - consulta o servidor pelo conteúdo associado à chave ch 
        # e escreve na saída o string e o valor, separados por uma vírgula, 
        # ou apenas -1, caso a chave não seja encontrada;
        if comando == 'C':
            chave = int(entrada[1])
            resposta = stub.consulta(diretorios_pb2.RequisicaoConsulta(chave=chave))
            if resposta.desc == '':
                print(-1)
            else:
                print(f'{resposta.desc},{resposta.valor:7.4f}')
        
        # R,nome,porto - dispara o procedimento de registro no servidor 
        # de diretórios independente, identificando o nome e o porto onde o 
        # servidor de integração se encontra. O cliente deve escrever 
        # o valor de retorno recebido. 
        # Esse comando pode ser executado qualquer número de vezes,
        # com identificadores de servidores possivelmente diferentes. 
        # Esse comando só faz sentido para usar a segunda parte.
        if comando == 'R':
            nome_int = entrada[1]
            porto_int = int(entrada[2])
            resposta = stub.registro(diretorios_pb2.RequisicaoRegistro(nome=nome_int, porto=porto_int))
            print(resposta.num)

        # T - sinaliza a terminação do servidor, 
        # escreve o valor de retorno e termina o cliente.
        if comando == 'T':
            resposta = stub.termino(diretorios_pb2.RequisicaoTermino())
            print(resposta.num)
            channel.close()

if __name__ == '__main__':
    run()