clean:
	@rm -rf diretorios_pb2_grpc.py diretorios_pb2.py integracao_pb2_grpc.py integracao_pb2.py

stubs:
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. diretorios.proto
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. integracao.proto

run_cli_dir:
	make stubs
	python3 client_dir.py $(arg)

run_serv_dir:
	make stubs
	python3 server_dir.py $(arg)

run_serv_int:
	make stubs
	python3 server_int.py $(arg)

run_cli_int:
	make stubs
	python3 client_int.py $(arg)