# Arquivo: broker/broker.py
# Função: Broker/Load Balancer (Extended Request-Reply)
# Padrão ZMQ: ROUTER/DEALER (com zmq.proxy)

import zmq
import sys

# --- Configurações de Endereço ---
# O Broker usa ROUTER para clientes (REQ)
FRONTEND_PORT = "5555" # Porta para os Clientes se conectarem (zmq.REQ)
# O Broker usa DEALER para servidores (REP)
BACKEND_PORT = "5556"  # Porta para os Servidores/Workers se conectarem (zmq.REP)

def run_broker():
    """
    Inicializa e executa o Broker ZMQ (ROUTER/DEALER) como um Load Balancer.
    """
    context = None
    client_socket = None
    server_socket = None

    try:
        context = zmq.Context()

        # 1. Configurar o Frontend (ROUTER):
        # Clientes (REQ) se conectarão aqui. O ROUTER lida com os IDs dos Clientes.
        client_socket = context.socket(zmq.ROUTER)
        client_socket.bind(f"tcp://*:{FRONTEND_PORT}")

        print(f"✅ Broker Frontend (ROUTER) ligado na porta {FRONTEND_PORT} (Para Clientes).")

        # 2. Configurar o Backend (DEALER):
        # Servidores (REP) se conectarão aqui. O DEALER faz o Load Balancing.
        server_socket = context.socket(zmq.DEALER)
        server_socket.bind(f"tcp://*:{BACKEND_PORT}")
        
        print(f"✅ Broker Backend (DEALER) ligado na porta {BACKEND_PORT} (Para Servidores).")
        
        print("---")
        print("Broker em execução... Roteando mensagens (CTRL+C para parar)")
        print("---")

        # 3. Executar o Proxy:
        # Encaminha requisições do ROUTER para o DEALER (e respostas no caminho inverso).
        zmq.proxy(client_socket, server_socket)
        
    # --- Tratamento de Erros ---
    except zmq.error.ContextTerminated:
        print("\n⚠️ Aviso: Broker encerrado pelo término do Contexto ZMQ.")
    except KeyboardInterrupt:
        # Captura o CTRL+C
        print("\n🛑 Broker encerrado pelo usuário (CTRL+C).")
    except Exception as e:
        print(f"\n❌ Erro Grave no Broker: {e}")
        print("Encerrando o sistema...")
    
    # --- Limpeza de Recursos ---
    finally:
        print("\nIniciando limpeza de recursos ZMQ...")
        if client_socket:
            client_socket.close()
        if server_socket:
            server_socket.close()
        if context:
            context.term()
        print("Limpeza concluída. 👋")


if __name__ == "__main__":
    run_broker()