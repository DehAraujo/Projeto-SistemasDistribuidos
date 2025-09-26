# src/proxy/main.py

import zmq
import sys

# --- Configurações ZMQ para o Forwarder ---

# Frontend: Onde os Publishers (Servidores) se conectam para ENVIAR mensagens.
# Este lado RECEBE a mensagem (XSUB), mas é o lado "front" para o servidor.
PUB_FRONTEND_PORT = 5557 

# Backend: Onde os Subscribers (Clientes) se conectam para RECEBER mensagens.
# Este lado ENVIA a mensagem (XPUB) para o cliente.
SUB_BACKEND_PORT = 5558 

def main():
    context = zmq.Context()

    # XSUB - FRONTEND (Recebe mensagens do Servidor)
    # Servidores (zmq.PUB) se conectarão a esta porta (5557)
    frontend = context.socket(zmq.XSUB)
    frontend.bind(f"tcp://*:{PUB_FRONTEND_PORT}")
    
    # XPUB - BACKEND (Distribui mensagens para o Cliente)
    # Clientes (zmq.SUB) se conectarão a esta porta (5558)
    backend = context.socket(zmq.XPUB)
    backend.bind(f"tcp://*:{SUB_BACKEND_PORT}")

    print(f"[Proxy] Iniciando Forwarder PUB/SUB...")
    print(f"[Proxy] Servidores (PUB) conectam-se a: tcp://*:{PUB_FRONTEND_PORT}")
    print(f"[Proxy] Clientes (SUB) conectam-se a: tcp://*:{SUB_BACKEND_PORT}")

    try:
        # zmq.proxy(frontend, backend)
        # O proxy encaminha mensagens do frontend para o backend, e vice-versa (assinaturas)
        zmq.proxy(frontend, backend)
        
    except zmq.error.ContextTerminated:
        print("\n[Proxy] Contexto encerrado.")
    except KeyboardInterrupt:
        print("\n[Proxy] Encerrado por usuário (Ctrl+C).")
    except Exception as e:
        print(f"[Proxy] Erro inesperado: {e}")
        
    finally:
        # Limpeza
        frontend.close()
        backend.close()
        context.term()
        sys.exit(0)

if __name__ == "__main__":
    main()