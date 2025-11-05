# Arquivo: proxy-pub.py
# Função: Proxy de Publicação de Mensagens (Alerta, Chat Público)
# Padrão ZMQ: XSUB/XPUB (com zmq.proxy)

import zmq
import sys

# --- Configurações de Endereço ---
# O Proxy de Publicação usa XSUB para receber mensagens do Server
# e XPUB para publicar (distribuir) para os Listeners/Monitores.
FRONTEND_PORT = "5557" # Porta para o Server enviar (XSUB)
BACKEND_PORT = "5558"  # Porta para os Listeners receberem (XPUB)

def run_proxy_pub():
    """
    Inicializa e executa o Proxy de Publicação ZMQ (XSUB/XPUB).
    """
    context = None
    frontend = None
    backend = None

    try:
        context = zmq.Context()

        # 1. Configurar o Frontend (XSUB - Entrada de Mensagens):
        # O Server se conectará aqui para ENVIAR mensagens.
        frontend = context.socket(zmq.XSUB)
        frontend.bind(f"tcp://*:{FRONTEND_PORT}")

        print(f" Proxy-PUB Frontend (XSUB) ligado na porta {FRONTEND_PORT} (Entrada do Servidor).")

        # 2. Configurar o Backend (XPUB - Saída de Mensagens):
        # Os Listeners (Monitor) se conectarão aqui para RECEBER mensagens.
        backend = context.socket(zmq.XPUB)
        # O XPUB lida automaticamente com o encaminhamento de assinaturas para o XSUB.
        backend.bind(f"tcp://*:{BACKEND_PORT}")
        
        print(f" Proxy-PUB Backend (XPUB) ligado na porta {BACKEND_PORT} (Saída para Listeners).")
        
        print("---")
        print("Proxy de Publicação em execução... (CTRL+C para parar)")
        print("---")

        # 3. Executar o Proxy:
        # O proxy encaminha mensagens do frontend (XSUB) para o backend (XPUB)
        # e mensagens de assinatura (Subscription) do backend para o frontend.
        zmq.proxy(frontend, backend)
        
    # --- Tratamento de Erros ---
    except zmq.error.ContextTerminated:
        print("\n Aviso: Proxy encerrado pelo término do Contexto ZMQ.")
    except KeyboardInterrupt:
        # Captura o CTRL+C
        print("\n Proxy de Publicação encerrado pelo usuário (CTRL+C).")
    except Exception as e:
        print(f"\n Erro Grave no Proxy de Publicação: {e}")
        print("Encerrando o sistema...")
    
    # --- Limpeza de Recursos ---
    finally:
        print("\nIniciando limpeza de recursos ZMQ...")
        if frontend:
            frontend.close()
        if backend:
            backend.close()
        if context:
            context.term()
        print("Limpeza concluída. ")


if __name__ == "__main__":
    # A chamada principal é encapsulada na função 'run_proxy_pub',
    # permitindo que o tratamento de exceções (como KeyboardInterrupt)
    # seja tratado de forma limpa DENTRO da função para garantir o 'finally'.
    run_proxy_pub()