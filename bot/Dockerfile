# Dockerfile para o Bot Ativo (Go/zeromq)

# Imagem base para compilação (builder)
FROM golang:1.22-alpine AS builder

# Instala dependências do sistema operacional para ZMQ
# O pacote 'go-zmq' usa a biblioteca C nativa do ZeroMQ
RUN apk add --no-cache zeromq-dev

# Define o diretório de trabalho
WORKDIR /app

# Copia o código-fonte do Bot
COPY bot.go .

# Instala a dependência Go do ZeroMQ e compila o binário
RUN go get [github.com/pebbe/zmq4](https://github.com/pebbe/zmq4) && \
    go build -o bot bot.go

# Imagem final de runtime (menor)
FROM alpine:3.19

# Instala a dependência ZMQ nativa na imagem de runtime
RUN apk add --no-cache zeromq

# Define o diretório de trabalho
WORKDIR /app

# Copia o binário compilado da fase 'builder'
COPY --from=builder /app/bot .

# Comando para executar o Bot compilado
CMD ["./bot"]