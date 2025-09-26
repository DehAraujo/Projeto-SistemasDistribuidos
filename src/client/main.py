import zmq

req_address = "broker"
req_port = 5555

sub_address = "proxy"
sub_port = 5558

context = zmq.Context()

req_socket = context.socket(zmq.REQ)
req_socket.connect(f"tcp://{req_address}:{req_port}")

sub_socket = context.socket(zmq.SUB)
sub_socket.connect(f"tcp://{sub_address}:{sub_port}")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
import zmq
import json
import time

# --- Configurações ZMQ ---
REQ_ADDRESS = "localhost"
REQ_PORT = 5555

SUB_ADDRESS = "localhost"
SUB_PORT = 5558 

# --- Inicialização dos Sockets (Variáveis Globais) ---
context = zmq.Context()

# Socket REQ: Para comandos interativos (REQ-REP)
req_socket = context.socket(zmq.REQ)
req_socket.connect(f"tcp://{REQ_ADDRESS}:{REQ_PORT}")

# Socket SUB: Para receber mensagens de chat (no futuro)
sub_socket = context.socket(zmq.SUB)
sub_socket.connect(f"tcp://{SUB_ADDRESS}:{SUB_PORT}")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "") 

print(f"[Client] Conectado ao Broker (REQ) em tcp://{REQ_ADDRESS}:{REQ_PORT}")
print(f"[Client] Conectado ao Proxy (SUB) em tcp://{SUB_ADDRESS}:{SUB_PORT}")


# --- FUNÇÃO PRINCIPAL PARA ENVIO REQ-REP (MULTIPART) ---
def send_request(req_socket, service, **kwargs):
    """
    Constrói e envia a requisição em dois frames (service e data) 
    e aguarda a resposta REP também em dois frames.
    """
    print(f"\n[Client] Enviando requisição: {service}...")
    
    # 1. PREPARAÇÃO DOS DADOS JSON
    data_payload = {"timestamp": int(time.time())}

    if service == "login":
        data_payload["user"] = kwargs.get("user")
    elif service == "channel":
        data_payload["channel"] = kwargs.get("channel")
        
    # Frame 1 (REQ): Service
    service_frame_req = service.encode('utf-8')
    
    # Frame 2 (REQ): Data (JSON string)
    data_frame_req = json.dumps(data_payload).encode('utf-8')
    
    # 2. ENVIA MENSAGEM MULTIPARTE (2 quadros)
    req_socket.send_multipart([service_frame_req, data_frame_req])
    
    # 3. RECEBE a resposta como MULTIPARTE (espera 2 quadros: Service e Data)
    try:
        # Nota: REQ/REP exige uma resposta antes de poder enviar novamente.
        response_parts = req_socket.recv_multipart()
    except zmq.error.ZMQError as e:
        # Erro de ZMQ (e.g., timeout, socket inválido)
        return {"service": service, "data": {"status": "erro", "description": f"Erro ZMQ ao receber resposta: {e}"}}


    if len(response_parts) < 2:
        print(f"[Client] Erro: Resposta incompleta do Broker (quadros: {len(response_parts)}).")
        return {"service": service, "data": {"status": "erro", "description": "Resposta incompleta do Broker."}}

    # Os quadros de resposta:
    service_frame_rep = response_parts[0]
    data_frame_rep = response_parts[1]
    
    # 4. DECODIFICA a resposta
    try:
        service_rep = service_frame_rep.decode('utf-8')
        response_data = json.loads(data_frame_rep.decode('utf-8'))
        
        # Reconstrói a mensagem completa no formato esperado para exibição: {"service": ..., "data": ...}
        response_msg = {"service": service_rep, "data": response_data}
        
    except Exception as e:
        print(f"[Client] Erro ao decodificar resposta do Broker: {e}")
        response_msg = {"service": service, "data": {"status": "erro", "description": f"Resposta inválida ou erro de JSON: {e}"}}
    
    return response_msg


# --- Função Principal de Execução ---

def main():
    # Assegurar que o socket REQ está livre (boa prática)
    try:
        req_socket.setsockopt(zmq.LINGER, 0)
    except Exception as e:
        print(f"[Client] Aviso ao definir LINGER: {e}")

    print("\n--- INICIANDO TESTES DA PARTE 1: REQ-REP ---")
    
    # 1. LOGIN DO USUÁRIO
    username = input(">>> Digite seu nome de usuário (ex: alice): ")
    response_login = send_request(req_socket, "login", user=username) 
    print(f"[1. LOGIN] Resposta:\n{json.dumps(response_login, indent=2)}")
    
    # Verifica se o login foi bem-sucedido para continuar os testes
    if response_login.get('data', {}).get('status') == 'sucesso':
        
        # 2. CRIAÇÃO DE CANAL
        channel_name = input(">>> Digite o nome do NOVO canal (ex: projetos_zeromq): ")
        response_channel = send_request(req_socket, "channel", channel=channel_name)
        print(f"\n[2. CRIAÇÃO DE CANAL] Resposta:\n{json.dumps(response_channel, indent=2)}")
        
        # 3. LISTAGEM DE USUÁRIOS CADASTRADOS
        response_users = send_request(req_socket, "users") 
        print(f"\n[3. LISTAR USUÁRIOS] Resposta:\n{json.dumps(response_users, indent=2)}")

        # 4. LISTAGEM DE CANAIS DISPONÍVEIS
        response_channels = send_request(req_socket, "channels") 
        print(f"\n[4. LISTAR CANAIS] Resposta:\n{json.dumps(response_channels, indent=2)}")
        
    else:
        print("\nLogin falhou. Encerrando testes REQ-REP.")

    # --- Limpeza Final ---
    req_socket.close()
    sub_socket.close()
    context.term()
    print("\n[Client] Conexões encerradas.")
    
if __name__ == "__main__":
    main()