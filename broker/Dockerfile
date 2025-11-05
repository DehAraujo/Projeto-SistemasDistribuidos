# Dockerfile para o Broker de Comandos (Python/pyzmq)

# Usa a base Python Alpine do professor, que é leve
FROM python:3.13.7-alpine3.21

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala a única dependência necessária (pyzmq)
RUN pip install pyzmq

# Copia o arquivo broker.py para o diretório /app
COPY broker.py .

# Comando para executar o Broker
# O nome do arquivo DEVE ser 'broker.py'
CMD ["python", "broker.py"]