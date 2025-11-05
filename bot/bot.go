// Arquivo: bot/bot.go
// Função: Bot Ativo. Envia comandos periódicos e escuta publicações.
// Padrões ZMQ: DEALER (para comandos) e SUB (para publicações)
// Linguagem: Go (Golang) - OBRIGATÓRIO para cumprir o requisito de 3 linguagens.
// Dependência: go get github.com/pebbe/zmq4

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"
    zmq "github.com/pebbe/zmq4"
)

// --- Configurações de Endereço ---
const BROKER_ADDRESS = "tcp://127.0.0.1:5555" 
const PROXY_PUB_ADDRESS = "tcp://127.0.0.1:5558"

// --- Estado do Bot ---
const BOT_USERNAME = "StatusBot_GO" 
const COMMAND_INTERVAL = 10 * time.Second // Envia o comando a cada 10 segundos

// --- Funções de Comunicação ---

// 1. Thread para Escutar Publicações (Monitoramento)
func listenPublications(subscriber *zmq.Socket) {
	fmt.Println("   [PUB/SUB] Escutando Alertas...")
	
	// Atraso para garantir que o socket SUB tenha tempo de se conectar ao XPUB
	time.Sleep(500 * time.Millisecond) 
	
	for {
		parts, err := subscriber.RecvMessageBytes(0)
		if err != nil {
			if err.Error() == "context terminated" {
				return
			}
			log.Printf("   [PUB/SUB] Erro ao receber mensagem: %v", err)
			continue
		}

		if len(parts) >= 2 {
			topic := string(parts[0])
			content := string(parts[1])

			if topic == "ALERTA" {
				fmt.Printf("    [ALERTA RECEBIDO]: %s\n", content)
			}
		}
	}
}

// 2. Thread para Enviar Comandos Periódicos
func sendPeriodicCommands(requester *zmq.Socket) {
	fmt.Printf("   [DEALER/ROUTER] Enviando comandos a cada %v...\n", COMMAND_INTERVAL)

	for {
		// Comando que o Bot Ativo envia
		cmd := "LIST" 
		request := map[string]interface{}{"cmd": cmd, "args": map[string]string{}}
		requestBytes, _ := json.Marshal(request)

		// Envia a requisição
		_, err := requester.Send(requestBytes, 0)
		if err != nil {
			log.Printf("   [DEALER/ROUTER] Erro ao enviar comando %s: %v", cmd, err)
			time.Sleep(COMMAND_INTERVAL)
			continue
		}
		
		// Espera a resposta (Síncrono)
		responseBytes, err := requester.RecvBytes(0)
		if err != nil {
			log.Printf("   [DEALER/ROUTER] Erro ao receber resposta para %s: %v", cmd, err)
		} else {
			var response map[string]string
			if err := json.Unmarshal(responseBytes, &response); err == nil {
				// Exibe a resposta do servidor de forma formatada
				fmt.Printf("    [RESPOSTA %s]: %s\n", response["status"], response["message"])
			} else {
				fmt.Printf("   [DEALER/ROUTER] Resposta inválida para %s: %s\n", cmd, string(responseBytes))
			}
		}

		time.Sleep(COMMAND_INTERVAL)
	}
}

// --- Função Principal ---
func main() {
	// 1. Configurar Conexão ZMQ
	context, err := zmq.NewContext()
	if err != nil {
		log.Fatal(err)
	}
	defer context.Term()

	// Socket de Comandos: DEALER
	commandSocket, err := context.NewSocket(zmq.DEALER)
	if err != nil {
		log.Fatal(err)
	}
	defer commandSocket.Close()
	commandSocket.Connect(BROKER_ADDRESS)

	// Socket de Publicações: SUB
	subSocket, err := context.NewSocket(zmq.SUB)
	if err != nil {
		log.Fatal(err)
	}
	defer subSocket.Close()
	subSocket.Connect(PROXY_PUB_ADDRESS)
	subSocket.SetSubscribe("") 

	fmt.Printf("\n🎉 Bot Ativo (%s) iniciado!\n", BOT_USERNAME)
	fmt.Printf(" Conectado ao Broker (Comandos) em %s\n", BROKER_ADDRESS)
	fmt.Printf(" Escutando Publicações em %s\n", PROXY_PUB_ADDRESS)
	
	// 2. Iniciar Threads
	
	// Thread 1: Escuta Alertas
	go listenPublications(subSocket)

	// Thread 2: Envia Comandos
	go sendPeriodicCommands(commandSocket)

	// 3. Bloquear a thread principal até receber um sinal de interrupção (CTRL+C)
	sigint := make(chan os.Signal, 1)
	signal.Notify(sigint, syscall.SIGINT, syscall.SIGTERM)
	<-sigint 

	fmt.Println("\nBot encerrado pelo usuário.")
}