FROM python:3.11-slim

LABEL maintainer="seu_email@exemplo.com"

# Atualize o sistema e instale pacotes básicos necessários
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    unixodbc-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Adicione a chave GPG e o repositório da Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Configure variáveis para aceitar o EULA automaticamente
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive

# Atualize o sistema novamente e remova pacotes conflitantes
RUN apt-get update && apt-get remove -y \
    libodbc2 \
    libodbcinst2 \
    unixodbc-common \
    && apt-get install -y --no-install-recommends \
    msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instale pacotes adicionais de desenvolvimento (opcional, dependendo do projeto)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure o diretório de trabalho (opcional)
WORKDIR /app

# Copie os arquivos da aplicação para o contêiner
COPY . /app

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando padrão para o contêiner (ajuste conforme necessário)
CMD ["python", "app.py"]