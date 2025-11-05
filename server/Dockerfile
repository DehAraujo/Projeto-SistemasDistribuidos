# Dockerfile para o Server de Lógica de Negócio (Python/pyzmq)

# Usa a base Python Alpine do professor, que é leve
FROM python:3.13.7-alpine3.21

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala a dependência pyzmq
RUN pip install pyzmq

# Copia o arquivo server.py para o diretório /app
COPY server.py .

# Comando para executar o Server
# O nome do arquivo DEVE ser 'server.py'
CMD ["python", "server.py"]