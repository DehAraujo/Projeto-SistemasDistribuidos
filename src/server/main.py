# src/server/main.py

import zmq
import json
import time

# Endereços usados no ambiente (Docker)
# Aqui ficam os "caminhos" para o servidor se conectar
BROKER_REQ_REP_ADDRESS = "tcp://localhost:5556"
PROXY_PUB_SUB_ADDRESS = "tcp://localhost:5557"

def main():
    context = zmq.Context()

    # 1. Cria um socket que vai responder às mensagens que chegam do Broker.
    #    (O servidor aqui funciona como um "funcionário" que recebe pedidos e manda respostas)
    rep_socket = context.socket(zmq.REP)
    rep_socket.connect(BROKER_REQ_REP_ADDRESS)
    print(f"[Server] Conectado ao Broker (REQ/REP) em {BROKER_REQ_REP_ADDRESS}")

    # 2. Cria um socket para mandar mensagens para todos os clientes.
    #    (É como um "alto-falante" do servidor para quem estiver ouvindo)
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect(PROXY_PUB_SUB_ADDRESS)
    print(f"[Server] Conectado ao Proxy (PUB) em {PROXY_PUB_SUB_ADDRESS}")
    
    # --- Loop principal: fica rodando sem parar para ouvir e responder ---
    print("[Server] Pronto para receber e responder mensagens...")

    while True:
        try:
            # 1. Recebe uma mensagem do Broker (em formato JSON)
            request_frame = rep_socket.recv()
            request_data = json.loads(request_frame.decode('utf-8'))
            service = request_data.get("service")
            
            print(f"[Server] Recebeu pedido: {service}")

            # 2. Aqui entraria a lógica real (login, listar usuários, etc).
            #    Por enquanto, só simulamos uma resposta de "sucesso".
            reply_data = process_server_logic(service, request_data.get("data", {}))
            
            # 3. Envia a resposta de volta para o Broker
            reply_frame = json.dumps(reply_data).encode('utf-8')
            rep_socket.send(reply_frame)

        except zmq.error.ContextTerminated:
            break
        except KeyboardInterrupt:
            break
        # Aqui poderia entrar um tratamento mais detalhado de erros

    # Fecha tudo antes de encerrar
    rep_socket.close()
    pub_socket.close()
    context.term()
    print("[Server] Encerrado.")

# Função que simula a "inteligência" do servidor
# (o que ele faz de verdade quando recebe uma requisição)
def process_server_logic(service, data):
    # Exemplo simples: sempre responde que deu certo, com a hora atual
    response = {"service": service, "data": {"status": "sucesso", "timestamp": int(time.time())}}
    return response

if __name__ == "__main__":
    main()
