import socket
import pickle
import struct
import time


# Retorna a lista de serviços oferecidos pelo servidor com nome e argumentos
def list_services():
    return call_remote_service("list_services")


# Função de adição
def add(x, y):
    return call_remote_service("add", x, y)


# Função de multiplicação
def multiply(x, y):
    return call_remote_service("multiply", x, y)


# Função de subtração
def subtract(x, y):
    return call_remote_service("subtract", x, y)

# Função de divisão
def divide(x, y):
    return call_remote_service("divide", x, y)

# Função de exponenciação
def power(x, y):
    return call_remote_service("power", x, y)

# Função de raiz quadrada
def sqrt(x):
    return call_remote_service("sqrt", x)

# Função para contar caracteres (len)
def char_count(s):
    return call_remote_service("char_count", s)
 
# Função de concatenação de strings
def concatenate(s1, s2):
    return call_remote_service("concatenate", s1, s2)

# Função para verificar se a string é um palíndromo
def is_palindrome(s):
    return call_remote_service("is_palindrome", s)

# Função de adição com atraso simulado para gerar timeout
def add_with_delay(x, y):
    return call_remote_service("add_delayed", x, y)

# Função que retorna dois valores
def double_response_service(x, y):
    return call_remote_service("double_response_service", x, y)

# Retorna a lista de serviços oferecidos pelo servidor com informações detalhadas
def list_services():
    return call_remote_service("list_services")


# Dicionário de funções stub
stub_services = {
    "add": add,
    "multiply": multiply,
    "subtract": subtract,
    "divide": divide,
    "power": power,
    "sqrt": sqrt,
    "char_count": char_count,
    "concatenate": concatenate,
    "is_palindrome": is_palindrome,
    "add_delayed": add_with_delay,
    "double_response_service": double_response_service,
    "list_services": list_services,
}


def call_selected_service(selected_service):
    try:
        print(f"Chamando serviço: {selected_service[0]}")
        if selected_service[0] in stub_services:
            stub_function = stub_services[selected_service[0]]
            args = []
            
            # Coleta os valores dos argumentos
            for arg_name in selected_service[1]:
                arg_value = input(f"Digite o valor para {arg_name}: ")
                # Converter para inteiro, se for possível
                try:
                    arg_value = int(arg_value)
                except ValueError:
                    pass

                # Converter para float, se for possível
                try:
                    arg_value = float(arg_value)
                except ValueError:
                    pass
            
                args.append(arg_value)
            
            # Chama a função de acordo com o dicionário de stubs
            result = stub_function(*args)
            
            print(f"Resultado: {result}")
        else:
            print("Função stub não encontrada para o serviço.")

    except Exception as e:
        print(f"Erro durante a chamada do serviço: {e}")

# Função para coletar a entrada do usuário
def get_user_input(prompt):
    return input(prompt)

# Função para chamar o serviço remoto
def call_remote_service(service_name, *args):
    # Configurações do socket
    host = "127.0.0.1"
    port = 5555
    timeout = 5
    max_attempts = 3

    # Tentar se conectar ao servidor
    for attempt in range(max_attempts):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(
            timeout
        ) 
        try:
            # Serializar dados para enviar ao servidor
            service_data = {"service": service_name, "args": args}
            frame_data = pickle.dumps(service_data)
            msg = struct.pack("Q", len(frame_data)) + frame_data

            # Enviar dados ao servidor
            client_socket.connect((host, port))
            client_socket.sendall(msg)

            # Receber resultado do servidor
            data = b""
            payload_size = struct.calcsize("Q")
            while len(data) < payload_size:
                packet = client_socket.recv(4 * 1024)  # 4K bytes de buffer
                if not packet:
                    break
                data += packet

            if not data:
                return "Erro: sem dados recebidos do servidor"

            # Deserializar dados recebidos
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4 * 1024)

            frame_data = data[:msg_size]
            result_data = pickle.loads(frame_data)

            # Retornar resultado da função chamada no servidor
            return result_data["result"]

        # Tratamento de erros
        except socket.timeout:
            print(f"Tentativa {attempt + 1}: Timeout. Tentando novamente...")
            time.sleep(1) # Aguardar 1 segundo antes de tentar novamente

        except Exception as e:
            print(f"Erro durante a chamada remota: {e}")
            return f"Erro: {e}"

        finally:
            client_socket.close()

    return "Erro: Excedido número máximo de tentativas."


if __name__ == "__main__":
    while True:
        # Listar serviços disponíveis
        services_list = list_services()

        print("Serviços disponíveis no servidor:")
        for i, service in enumerate(services_list, start=1):
            print(f"{i}. {service[0]}")

        try:
            selected_index = (
                int(get_user_input("Selecione o número do serviço desejado: ")) - 1
            )
            selected_service = services_list[selected_index]
            call_selected_service(selected_service)
        except (ValueError, IndexError):
            print("Opção inválida. Por favor, selecione novamente.")

        user_input = get_user_input("Deseja chamar outro serviço? (S/N): ").lower()
        if user_input != "s":
            break
