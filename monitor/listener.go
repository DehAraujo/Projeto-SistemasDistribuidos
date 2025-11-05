// Arquivo: monitor/listener.go
// Função: Listener de mensagens públicas (Monitor Web)
// Padrão ZMQ: SUB (Subscriber)
// Dependência: go get github.com/pebbe/zmq4

package main

import (
    "fmt"
    "log"
    "os"
    "os/signal"
    "syscall"
    zmq "github.com/pebbe/zmq4"
)

// --- Configurações de Endereço ---
const PROXY_PUB_ADDRESS = "tcp://127.0.0.1:5558" // Conecta no Backend do Proxy-PUB (XPUB)

func main() {
    // 1. Inicializar o socket SUB
    subscriber, err := zmq.NewSocket(zmq.SUB)
    if err != nil {
        log.Fatalf("Erro ao criar socket ZMQ: %v", err)
    }
    defer subscriber.Close()

    // 2. Conectar ao Proxy-PUB
    err = subscriber.Connect(PROXY_PUB_ADDRESS)
    if err != nil {
        log.Fatalf("Erro ao conectar ao Proxy-PUB em %s: %v", PROXY_PUB_ADDRESS, err)
    }

    // 3. Assinar todos os tópicos (tópico vazio)
    // Isso garante que o Listener receba todas as mensagens publicadas.
    // Se quiséssemos apenas alertas, usaríamos subscriber.SetSubscribe("ALERTA")
    subscriber.SetSubscribe("")

    fmt.Printf("✅ Monitor Listener conectado ao Proxy-PUB em %s\n", PROXY_PUB_ADDRESS)
    fmt.Println("Monitor em execução, aguardando mensagens públicas... (CTRL+C para parar)")

    // Configurar o tratamento de sinais (CTRL+C)
    sigint := make(chan os.Signal, 1)
    signal.Notify(sigint, syscall.SIGINT, syscall.SIGTERM)

    // Loop de escuta de mensagens
    for {
        select {
        case <-sigint:
            // Recebeu sinal de interrupção
            fmt.Println("\nListener encerrado pelo usuário.")
            return

        default:
            // Recebe a mensagem em partes (tópico, conteúdo)
            parts, err := subscriber.RecvMessageBytes(0) 
            if err != nil {
                // Pode acontecer em um shutdown, mas tratamos de forma simples
                if err != nil && err.Error() != "interrupted" {
                    log.Printf("Erro ao receber mensagem: %v", err)
                }
                continue
            }
            
            if len(parts) >= 2 {
                topic := string(parts[0])
                content := string(parts[1])

                // Exemplo de exibição formatada
                if topic == "ALERTA" {
                    fmt.Printf("🔔 [%s] %s\n", topic, content)
                } else {
                    fmt.Printf("📦 [MENSAGEM] Tópico: %s, Conteúdo: %s\n", topic, content)
                }
            } else {
                 fmt.Printf("Mensagem recebida com formato inválido: %v\n", parts)
            }
        }
    }
}