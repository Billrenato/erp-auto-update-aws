# Imagem base leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas os arquivos de dependência primeiro (melhora cache do Docker)
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir python-multipart

# Copia o restante do código
COPY . .

# Expõe a porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


