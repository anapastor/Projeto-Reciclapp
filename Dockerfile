# Usa a imagem base do Python
FROM python:3.11-slim

# Informação do mantenedor (opcional)
LABEL maintainer="seu_email@exemplo.com"

# Atualiza os pacotes e instala ferramentas necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gpg \
    gnupg2 \
    unixodbc-dev \
    gcc \
    g++ \
    make \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos da aplicação para a imagem
COPY . .

# Instala as dependências Python (inclui o mysql-connector-python)
RUN pip install --no-cache-dir -r requirements.txt mysql-connector-python

# Exponha a porta 5000 para a aplicação
EXPOSE 5000

# Define o comando padrão para iniciar a aplicação
CMD ["python", "API.py"]