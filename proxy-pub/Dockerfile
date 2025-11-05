# Dockerfile para o Proxy de Publicação (Python/pyzmq)

# Usa a base Python Alpine do professor, que é leve
FROM python:3.13.7-alpine3.21

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala a dependência pyzmq
RUN pip install pyzmq

# Copia o arquivo proxy_pub.py para o diretório /app
COPY proxy_pub.py .

# Comando para executar o Proxy-PUB
# O nome do arquivo DEVE ser 'proxy_pub.py'
CMD ["python", "proxy_pub.py"]