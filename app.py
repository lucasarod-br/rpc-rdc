#Importações
import socket
import pickle
import threading
import struct
import time 

# Função para simular dados duplicados
def double_response_service(x, y):
    return x + y, x + y

# Função para simular timeout do servidor
def add_with_delay(x, y):
    time.sleep(10)  # Atraso de 10 segundos
    return x + y



# Definindo o dicionário de serviços com função (lambda) e parâmetros
services = {
    "add": {"function": lambda x, y: x + y, "params": ["Número 1", "Número 2"]},
    "add_delayed": {"function": lambda x, y: add_with_delay(x, y), "params": ["Número 1", "Número 2"]},
    "multiply": {"function": lambda x, y: x * y, "params": ["Número 1", "Número 2"]},
    "subtract": {"function": lambda x, y: x - y, "params": ["Número 1", "Número 2"]},
    "divide": {"function": lambda x, y: x / y if y != 0 else "Não é possível dividir por 0", "params": ["Numerador", "Denominador"]},
    "power": {"function": lambda x, y: x ** y, "params": ["Base", "Expoente"]},
    "sqrt": {"function": lambda x: x ** 0.5 if x >= 0 else "Não é possível tirar a raiz de número negativo.", "params": ["Radicando"]},
    "char_count": {"function": lambda s: len(s), "params": ["String"]},
    "concatenate": {"function": lambda s1, s2: s1 + s2, "params": ["String 1", "String 2"]},
    "is_palindrome": {"function": lambda s: s == s[::-1], "params": ["String"]},
    "list_services": {"function": lambda: [(name, info["params"]) for name, info in services.items()], "params": []},
    "double_response_service": {"function": double_response_service, "params": ["Número 1", "Número 2"]}
}

# Tratamento de solicitações do client
def handle_client(client_socket):
    try:
        while True:
            # Receber dados do cliente
            data = b""
            payload_size = struct.calcsize("Q")
            while len(data) < payload_size:
                packet = client_socket.recv(4 * 1024)
                if not packet:
                    break
                data += packet

            if not data:
                break

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4 * 1024)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Deserializar dados e chamar o serviço solicitado
            service_data = pickle.loads(frame_data)
            service_name = service_data["service"]
            args = service_data.get("args", ())
            service_info = services.get(service_name, {"function": lambda *args: "Invalid service"})
            service_function = service_info["function"]
            result = service_function(*tuple(args))

            if service_name == "double_response_service":
                # Chamada com resposta dupla
                response1, response2 = result
                result_data1 = pickle.dumps({"result": response1})
                result_msg1 = struct.pack("Q", len(result_data1)) + result_data1
                client_socket.sendall(result_msg1)

                result_data2 = pickle.dumps({"result": response2})
                result_msg2 = struct.pack("Q", len(result_data2)) + result_data2
                client_socket.sendall(result_msg2)
            else:
                # Chamada regular
                result_data = pickle.dumps({"result": result})
                result_msg = struct.pack("Q", len(result_data)) + result_data
                client_socket.sendall(result_msg)

    except Exception as e:
        print(f"Erro durante o manuseio do cliente: {e}")

    finally:
        client_socket.close()

# Execução do servidor
def run_server():
    # Configurações do servidor
    host = "127.0.0.1"
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Servidor escutando em {host}:{port}")

    try:
        while True:
            # Aceitar conexão do cliente
            client_socket, addr = server_socket.accept()
            print(f"Conexão aceita de {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

    except KeyboardInterrupt:
        print("\nServidor encerrado.")

    finally:
        # Fechar o socket do servidor
        server_socket.close()


if __name__ == "__main__":
    run_server()
