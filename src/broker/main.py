import zmq
import json
import os
import time

# --- 2. VARIÁVEIS GLOBAIS E PERSISTÊNCIA ---
# Configuração do caminho do arquivo de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'data.json')

server_data = {"users": {}, "channels": {}}

# --- 3. FUNÇÕES DE PERSISTÊNCIA ---
def load_data():
    global server_data
    print(f"[Broker] Tentando carregar dados de: {DATA_FILE_PATH}")
    if os.path.exists(DATA_FILE_PATH):
        try:
            with open(DATA_FILE_PATH, 'r') as f:
                server_data = json.load(f)
            print("Dados carregados com sucesso!")
        except Exception as e:
            print(f"ERRO ao carregar dados: {e}. Iniciando com dados vazios.")
    else:
        print("Arquivo de dados não encontrado. Iniciando com dados vazios.")
    return server_data

def save_data():
    try:
        with open(DATA_FILE_PATH, 'w') as f:
            json.dump(server_data, f, indent=4)
    except Exception as e:
        print(f"ERRO ao salvar dados: {e}")

# --- 4. FUNÇÃO DE LÓGICA DE NEGÓCIO ---
# Aceita a identidade do cliente, o quadro de serviço e o quadro de dados
def handle_request(client_address, service_frame, data_frame):
    global server_data
    service = "unknown"
    
    try:
        # 1. DECODIFICA o primeiro quadro para obter o serviço
        service = service_frame.decode('utf-8') 
        
        # 2. Decodifica o segundo quadro de dados (com tratamento de quadro vazio)
        if data_frame:
            data = json.loads(data_frame.decode('utf-8'))
        else:
            # Payload básico se o quadro estiver vazio
            data = {"timestamp": int(time.time())} 
        
        response_data = {"status": "sucesso", "timestamp": int(time.time())}

        # --- Lógica de Login/Channel/Users/Channels ---
        if service == "login":
            user = data.get("user")
            if not user:
                response_data.update({"status": "erro", "description": "Nome de usuário inválido."})
            elif user in server_data["users"]:
                response_data.update({"status": "erro", "description": f"Usuário '{user}' já está cadastrado ou online."})
            else:
                server_data["users"][user] = {"status": "online", "client_address": client_address.hex()}
                save_data()
                response_data["description"] = f"Usuário '{user}' logado com sucesso."
                
        elif service == "users":
            response_data["users"] = list(server_data["users"].keys())
            
        elif service == "channel":
            channel = data.get("channel")
            if not channel:
                response_data.update({"status": "erro", "description": "Nome de canal inválido."})
            elif channel in server_data["channels"]:
                response_data.update({"status": "erro", "description": f"Canal '{channel}' já existe."})
            else:
                server_data["channels"][channel] = {"creator": "system", "members": []}
                save_data()
                response_data["description"] = f"Canal '{channel}' criado com sucesso."
                
        elif service == "channels":
            response_data["channels"] = list(server_data["channels"].keys())
            
        else:
            response_data.update({"status": "erro", "description": f"Serviço '{service}' não reconhecido."})

        # Remove a chave 'status' para serviços de listagem que não a utilizam na resposta final
        if service in ["users", "channels"] and "status" in response_data:
            del response_data["status"]

    except Exception as e:
        print(f"[Broker] ERRO DE PROCESSAMENTO ({service}): {e}")
        response_data = {
            "status": "erro", 
            "timestamp": int(time.time()), 
            "description": f"Erro interno do Broker ao processar '{service}': {e}"
        }
        # Garante que o serviço retorne o nome do serviço para o cliente entender o erro
        service = service or "unknown" 

    # MUDANÇA CRUCIAL: Retorna os dois quadros de resposta (Service e Data JSON)
    frame_service_rep = service.encode('utf-8')
    frame_data_rep = json.dumps(response_data).encode('utf-8')
    
    return frame_service_rep, frame_data_rep # Retorna uma tupla de quadros


# --- 5. FUNÇÃO PRINCIPAL (MAIN) ---
def main():
    global server_data
    # Carrega os dados iniciais
    server_data = load_data() 
    print(f"Status Inicial do Broker: {len(server_data['users'])} usuários, {len(server_data['channels'])} canais.")
    
    context = zmq.Context()
    
    # O socket ROUTER recebe requisições de clientes REQ
    client_socket = context.socket(zmq.ROUTER)
    client_socket.bind("tcp://*:5555")

    poller = zmq.Poller()
    poller.register(client_socket, zmq.POLLIN)

    print("[Broker] Aguardando requisições na porta 5555 (Clientes)...")

    while True:
        try:
            socks = dict(poller.poll(timeout=500)) 
            
            if socks:
                if client_socket in socks and socks[client_socket] == zmq.POLLIN:
                    
                    # O ROUTER recebe 4 quadros (Identidade, Vazio, Serviço, Dados)
                    message = client_socket.recv_multipart()
                    
                    client_address = message[0]
                    # message[1] é o quadro vazio b''
                    
                    # Garantia contra mensagens incompletas (caso o cliente tenha enviado menos quadros)
                    if len(message) < 4:
                        print(f"[Broker] ERRO: Mensagem incompleta recebida do endereço {client_address.hex()}. Ignorando.")
                        continue # Volta ao loop, esperando a próxima mensagem
                    
                    service_frame = message[2]
                    data_frame = message[3]
                    
                    # Log de debug
                    print(f"\n[Broker DEBUG] RECEBIDO do endereço {client_address.hex()}: SERVICE={service_frame.decode('utf-8')}, DATA={data_frame.decode('utf-8')}") 

                    # Processa a requisição e recebe a resposta em dois quadros
                    frame_service_rep, frame_data_rep = handle_request(client_address, service_frame, data_frame)
                    
                    # ENVIA A RESPOSTA MULTIPART: [Endereço, Vazio, Service, Data]
                    client_socket.send_multipart([client_address, b'', frame_service_rep, frame_data_rep])
                    
        except KeyboardInterrupt:
            print("\n[Broker] Encerrado por usuário (Ctrl+C).")
            break
        except Exception as e:
            print(f"[Broker] Erro inesperado no loop: {e}")
            break

    client_socket.close()
    context.term()
    print("[Broker] Encerrado.")

# --- 6. EXECUÇÃO ---
if __name__ == "__main__":
    main()