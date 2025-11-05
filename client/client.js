// Arquivo: client/client.js
// Função: Cliente CLI interativo para enviar comandos e escutar mensagens públicas
// Linguagem: Node.js (JavaScript) 
// Dependências: zeromq (npm install zeromq)

const zmq = require('zeromq');
const readline = require('readline');

// --- Configurações de Endereço ---
const BROKER_ADDRESS = "tcp://127.0.0.1:5555"; 
const PROXY_PUB_ADDRESS = "tcp://127.0.0.1:5558"; 

// 1. Configurar Interface de Linha de Comando (CLI)
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// 2. Conectar ao Broker para Comandos (DEALER)
const commandSocket = zmq.socket('dealer');
commandSocket.connect(BROKER_ADDRESS);

// 3. Conectar ao Proxy-PUB para Escutar Mensagens (SUB)
const subSocket = zmq.socket('sub');
subSocket.connect(PROXY_PUB_ADDRESS);
subSocket.subscribe(''); // Assina todos os tópicos

console.log(`\n Cliente Node.js iniciado!`);
console.log(` Conectado ao Broker (Comandos) em ${BROKER_ADDRESS}`);
console.log(` Escutando Publicações em ${PROXY_PUB_ADDRESS}\n`);

// --- Funções de Comunicação ---

// A. Escutando Respostas do Broker
commandSocket.on('message', (msg) => {
    // No lado do DEALER/CLIENTE, a mensagem é apenas o conteúdo da resposta
    const response = JSON.parse(msg.toString());
    
    if (response.status === 'success') {
        console.log(`\n[RESPOSTA OK] ${response.message}`);
    } else {
        console.log(`\n[ERRO] ${response.message}`);
    }
    promptUser(); 
});


// B. Escutando Publicações do Proxy-PUB
subSocket.on('message', (topic, message) => {
    const topicStr = topic.toString();
    const messageStr = message.toString();

    // Mensagens de Alerta (Ex: login de novo usuário)
    if (topicStr === 'ALERTA') {
        console.log(`\n [ALERTA RECEBIDO]: ${messageStr}`);
    } 
    promptUser(); 
});


// C. Função de Envio de Comandos
function sendCommand(cmd, args = {}) {
    const request = { cmd, args };
    const requestStr = JSON.stringify(request);
    commandSocket.send(Buffer.from(requestStr));
}


// --- Interface de Usuário ---

function promptUser() {
    rl.question('Digite um comando (ex: login [nome] ou help): ', (input) => {
        const parts = input.trim().split(' ');
        const cmd = parts[0].toUpperCase();
        const arg1 = parts[1];

        if (cmd === 'EXIT' || cmd === 'QUIT') {
            commandSocket.close();
            subSocket.close();
            rl.close();
            console.log('Cliente encerrado.');
            return;
        }

        if (cmd === 'LOGIN' && arg1) {
            sendCommand('LOGIN', { username: arg1 });
        } else if (cmd === 'HELP') {
            console.log("\nComandos disponíveis:");
            console.log("  login [seu_nome]  -> Tenta fazer login e envia um alerta.");
            console.log("  exit / quit       -> Encerra o cliente.");
            promptUser();
        } else {
            console.log(`Comando inválido ou incompleto. Digite 'help' para comandos.`);
            promptUser();
        }
    });
}

// Inicia o loop
promptUser();

// Tratamento de interrupção
process.on('SIGINT', () => {
    commandSocket.close();
    subSocket.close();
    rl.close();
    console.log('\nCliente encerrado pelo usuário.');
    process.exit();
});