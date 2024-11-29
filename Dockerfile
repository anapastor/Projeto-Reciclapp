# Use uma imagem base com Python
FROM python:3.9-slim

# Instale dependências do sistema necessárias para o pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    libpq-dev \
    && apt-get clean

# Instale as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação
COPY . /app
WORKDIR /app

# Comando para rodar a aplicação
CMD ["python", "API.py"]