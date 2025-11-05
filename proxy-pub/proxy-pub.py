# Arquivo: proxy-pub.py
# Função: Proxy de Publicação de Mensagens (Alerta, Chat Público)
# Padrão ZMQ: XSUB/XPUB (com zmq.proxy)

import zmq

# --- Configurações de Endereço ---
# O Proxy de Publicação usa XSUB para receber mensagens do servidor
# e XPUB para redistribuí-las aos listeners/monitores.
FRONTEND_PORT = "5557"  # Porta para o servidor enviar (XSUB)
BACKEND_PORT = "5558"   # Porta para os listeners receberem (XPUB)


def run_proxy_pub():
    """
    Inicializa e executa o Proxy de Publicação ZMQ (XSUB/XPUB).
    """
    context = None
    frontend = None
    backend = None

    try:
        context = zmq.Context()

        # 1. Frontend (XSUB) — recebe mensagens do servidor
        frontend = context.socket(zmq.XSUB)
        frontend.bind(f"tcp://*:{FRONTEND_PORT}")
        print(f" Proxy-PUB Frontend (XSUB) ligado na porta {FRONTEND_PORT} (entrada do servidor).")

        # 2. Backend (XPUB) — envia mensagens aos listeners
        backend = context.socket(zmq.XPUB)
        backend.bind(f"tcp://*:{BACKEND_PORT}")
        print(f" Proxy-PUB Backend (XPUB) ligado na porta {BACKEND_PORT} (saída para listeners).")

        print("\n---")
        print("Proxy de Publicação em execução... (CTRL+C para encerrar)")
        print("---\n")

        # 3. Executar o proxy
        zmq.proxy(frontend, backend)

    except zmq.error.ContextTerminated:
        print("\nAviso: Proxy encerrado pelo término do contexto ZMQ.")
    except KeyboardInterrupt:
        print("\nProxy de Publicação encerrado pelo usuário (CTRL+C).")
    except Exception as e:
        print(f"\nErro no Proxy de Publicação: {e}")
    finally:
        print("\nEncerrando e limpando recursos ZMQ...")
        if frontend:
            frontend.close()
        if backend:
            backend.close()
        if context:
            context.term()
        print("Limpeza concluída com sucesso.")


if __name__ == "__main__":
    run_proxy_pub()
