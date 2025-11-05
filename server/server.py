# Arquivo: server/server.py
# Função: Servidor/Worker (REQ/REP) e Publisher (PUB/SUB)
# Conexões: REP (para Broker) e PUB (para Proxy de Publicação)

import zmq
import time
import sys
import random

# --- Configurações de Endereço ---
# O Server é um WORKER, conecta-se ao BROKER (REP)
BROKER_ADDRESS = "tcp://localhost:5556" # Endereço do Broker/Router
# O Server é um PUBLISHER, conecta-se ao PROXY (PUB)
PROXY_ADDRESS = "tcp://localhost:5557" # Endereço do Proxy de Publicação/XSUB

def run_server(server_id):
    """
    Inicializa o Server, conecta-se ao Broker e ao Proxy e inicia o loop de processamento.
    """
    context = None
    rep_socket = None
    pub_socket = None
    
    print(f" Servidor ID: {server_id} iniciando...")

    try:
        context = zmq.Context()

        # 1. Socket de Resposta (REP) - Conecta-se ao Broker
        # O Server atua como um Worker que recebe REQ e envia REP
        rep_socket = context.socket(zmq.REP)
        rep_socket.connect(BROKER_ADDRESS)
        print(f" REP Socket conectado ao Broker: {BROKER_ADDRESS}")

        # 2. Socket de Publicação (PUB) - Conecta-se ao Proxy
        # O Server atua como Publisher para enviar alertas ao Proxy XSUB
        pub_socket = context.socket(zmq.PUB)
        pub_socket.connect(PROXY_ADDRESS)
        print(f" PUB Socket conectado ao Proxy: {PROXY_ADDRESS}")

        # Garante que a conexão PUB/SUB esteja estabelecida antes de publicar
        time.sleep(1) 
        print("\nServidor pronto para processar requisições...")

        # --- Loop Principal de Processamento ---
        while True:
            # 1. Receber Requisição do Broker (Cliente)
            message = rep_socket.recv_string()
            print(f"\n[REP] ⬅ Recebido comando: '{message}'")

            # 2. Simular Processamento e Lógica
            time.sleep(random.uniform(0.1, 0.5)) # Simula trabalho
            
            response = f"RESPOSTA do {server_id}: Comando '{message}' processado."
            
            # 3. Enviar Resposta de volta ao Broker (Cliente)
            rep_socket.send_string(response)
            print(f"[REP]  Resposta enviada ao Cliente: '{response}'")

            # 4. Gerar e Publicar Alerta (para Listeners/Monitors)
            # O formato é TÓPICO MENSAGEM
            if "ALERTA" in message.upper():
                topic = "ALERTA"
                pub_message = f"ALERTA ALTO: {server_id} processou a requisição!"
            else:
                topic = "CHAT"
                pub_message = f"CHAT: {server_id} finalizou um trabalho comum."

            # Publica o tópico e a mensagem (separados por espaço)
            full_pub_message = f"{topic} {pub_message}"
            pub_socket.send_string(full_pub_message)
            print(f"[PUB]  Publicado Alerta ({topic}): '{pub_message}'")
            print("-" * 40)

    except zmq.error.ContextTerminated:
        print(f"\n Servidor {server_id} encerrado pelo término do Contexto ZMQ.")
    except KeyboardInterrupt:
        print(f"\n Servidor {server_id} encerrado pelo usuário (CTRL+C).")
    except Exception as e:
        print(f"\n Erro Grave no Servidor {server_id}: {e}")
    
    # --- Limpeza de Recursos ---
    finally:
        print(f"\nIniciando limpeza de recursos ZMQ para {server_id}...")
        if rep_socket:
            rep_socket.close()
        if pub_socket:
            pub_socket.close()
        if context:
            context.term()
        print("Limpeza concluída. ")


if __name__ == "__main__":
    # Permite passar o ID do servidor como argumento
    server_id = "SERVER_A"
    if len(sys.argv) > 1:
        server_id = sys.argv[1]
    
    run_server(server_id)