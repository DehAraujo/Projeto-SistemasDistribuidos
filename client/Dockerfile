# Dockerfile para o Cliente CLI (Node.js/zeromq)

# Usamos uma imagem Node.js base com Alpine (leve)
FROM node:21-alpine

# Instalação das dependências do ZeroMQ. 
# O zeromq do Node.js precisa de dependências do sistema operacional para compilar.
# 'zmq' é o pacote essencial para ZeroMQ.
RUN apk add --no-cache python3 make g++ zeromq-dev

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo package.json (gerado após o npm init -y) e o client.js
COPY package.json package-lock.json ./
COPY client.js .

# Instala a dependência zeromq
RUN npm install

# Comando para executar o Cliente Node.js
# Necessita de 'stdin_open: true' e 'tty: true' no docker-compose.yml para interagir.
CMD ["node", "client.js"]