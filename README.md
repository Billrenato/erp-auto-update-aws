# ERP Auto Update System

Sistema de atualização automática para terminais ERP, desenvolvido em Python 3.11 e preparado para rodar via AWS (EC2 + S3).

O projeto permite que múltiplos terminais atualizem automaticamente seus executáveis (.exe) e 
arquivos auxiliares através de uma API centralizada, garantindo distribuição eficiente e controle de versões.

===============================================================================
1. VISÃO GERAL
===============================================================================

CLIENTE (Python/EXE):
- Verifica a versão instalada (version.txt)
- Consulta a API de atualização
- Faz download do arquivo .zip da nova versão
- Extrai automaticamente os arquivos no diretório configurado (C:\sistema\bin)
- Atualiza o version.txt e inicia o ERP (Vnd.exe)

SERVIDOR (Python + FastAPI):
- Endpoint /check_update → informa se há nova versão
- Endpoint /download/{arquivo} → fornece o .zip hospedado no S3
- Configuração de hospedagem: AWS EC2 (Docker + Gunicorn/Uvicorn)
- Armazenamento de versões: AWS S3 Bucket
      

===============================================================================
2. ESTRUTURA DO PROJETO
===============================================================================

erp-auto-update-aws/
│
├── api/
│   ├── Dockerfile              # Configuração de build e deploy
│   ├── main.py/               # API principal (FastAPI/Flask) vai rodar na aws tbm
│   └── requirements.txt       # Dependências do servidor
│
├── storage/
│   ├── manifest.json    # Cliente Python
│   ├── v1.0.5.zip       # Arquivo vai ficar no s3 aws
│                  
│
├── client_simulator.py        # esse arquivo vai ficar no terminal do cliente      
├── docker-compose.yml         # Configuração de container (opcional)
└── README.md                  

===============================================================================
3. TECNOLOGIAS
===============================================================================

- Python 3.11
- FastAPI ou Flask (para a API)
- Requests, ZipFile, io
- AWS S3 (armazenamento das versões)
- AWS EC2 (execução da API)
- PyInstaller (geração do executável .exe)
- Docker (empacotamento e deploy automatizado)

===============================================================================
4. CONFIGURAÇÃO DO CLIENTE
===============================================================================

1. Configure o diretório de instalação no código:
   INSTALL_DIR = r"C:\sistema\bin"

2. Gere o executável:
   pyinstaller --onefile client_simulator.py

3. Copie o executável gerado para os terminais que farão a atualização automática.

===============================================================================
5. DEPLOY NA AWS
===============================================================================

1. Crie um bucket S3:
   Nome: erp-auto-update-files
   Estrutura: versions/v1.0.1.zip

2. Configure o servidor na instância EC2:
   docker build -t erp-update-server .
   docker run -d -p 8080:8080 erp-update-server

3. Endpoints disponíveis:
   /check_update?version=1.0.0     → Retorna JSON informando se há nova versão
   /download/v1.0.1.zip            → Fornece o arquivo compactado da nova versão

===============================================================================
6. TESTE LOCAL
===============================================================================

# Rodar o servidor localmente
python server/app.py

# Executar o cliente simulador
python client/client_simulator.py

===============================================================================
7. SEGURANÇA E BOAS PRÁTICAS
===============================================================================

- Utilize hash MD5 ou SHA256 para validar a integridade dos arquivos ZIP.
- Configure HTTPS (via Nginx ou CloudFront).
- Restrinja permissões de gravação em C:\piracaiasoft\bin.
- Armazene as chaves e tokens AWS em variáveis de ambiente.
- Implemente log de atualização (update.log) para auditoria.

===============================================================================
8. PRÓXIMOS PASSOS
===============================================================================

1. Configurar e testar:
   - API rodando na AWS EC2
   - Arquivos .zip hospedados no S3
2. Validar atualização em múltiplos terminais
3. Implementar rollback automático em caso de falha
4. Adicionar verificação de integridade do executável
5. Configurar monitoramento com CloudWatch

===============================================================================



#!/bin/bash
# ============================================================
# 🚀 ERP AUTO UPDATE - DEPLOY COMPLETO COM FASTAPI, DOCKER E AWS S3
# ============================================================
# Script de automação para configurar e publicar o sistema ERP Auto Update
# Autor: QRtouch
# Versão: 1.0.0

# ============================================================
# 1️⃣ ATUALIZAÇÃO DO SISTEMA E INSTALAÇÃO DE DEPENDÊNCIAS
# ============================================================
echo -e "${ARROW} ${YELLOW}Atualizando pacotes do sistema...${RESET}"
sudo apt update -y && sudo apt upgrade -y
echo -e "${CHECK} Sistema atualizado!"

echo -e "${ARROW} ${YELLOW}Instalando Docker e Docker Compose...${RESET}"
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
echo -e "${CHECK} Docker instalado e iniciado!"

# ============================================================
# 2️⃣ CLONAR O REPOSITÓRIO
# ============================================================
REPO_URL="https://github.com/<usuario>/erp-auto-update-aws.git"
echo -e "${ARROW} ${YELLOW}Clonando repositório do GitHub...${RESET}"
git clone "$REPO_URL" || { echo -e "${ERROR} Falha ao clonar repositório!"; exit 1; }
cd erp-auto-update-aws || exit
echo -e "${CHECK} Repositório clonado com sucesso!"

# ============================================================
# 3️⃣ CONFIGURAR VARIÁVEIS AWS
# ============================================================
echo -e "${CLOUD} ${YELLOW}Configurando variáveis de ambiente AWS...${RESET}"

read -p "🪪 AWS_ACCESS_KEY_ID: " AWS_ACCESS_KEY_ID
read -p "🔑 AWS_SECRET_ACCESS_KEY: " AWS_SECRET_ACCESS_KEY

export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export AWS_REGION="sa-east-1"
export S3_BUCKET="erp-auto-update"

echo -e "${CHECK} Variáveis configuradas!"

# ============================================================
# 4️⃣ ESTRUTURA DO PROJETO
# ============================================================

cat > api/requirements.txt << 'EOF'
fastapi
uvicorn
boto3
EOF

cat > api/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker-compose.yml << 'EOF'
services:
  update_api:
    build: ./api
    ports:
      - "8080:8000"
    environment:
      - AWS_REGION=sa-east-1
      - S3_BUCKET=erp-auto-update
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
EOF

cat > manifest.json << 'EOF'
{
  "update": true,
  "version": "1.0.6",
  "file": "v1.0.6.zip"
}
EOF

echo -e "${CHECK} Estrutura criada!"

# ============================================================
# 5️⃣ CONSTRUIR E EXECUTAR CONTAINER
# ============================================================
echo -e "${DOCKER} ${YELLOW}Construindo imagem Docker e iniciando container...${RESET}"
sudo docker compose up -d
echo -e "${CHECK} Container iniciado com sucesso!"

# ============================================================
# 6️⃣ TESTE DA API
# ============================================================
IP=$(curl -s http://checkip.amazonaws.com)
echo -e "${ARROW} ${YELLOW}Testando API local...${RESET}"
sleep 5
curl "http://${IP}:8080/check_update?version=1.0.5"

# ============================================================
# 7️⃣ LOGS
# ============================================================
echo -e "${ARROW} ${YELLOW}Exibindo logs do container...${RESET}"
sudo docker logs -f erp-auto-update-aws-update_api-1 &

# ============================================================
# 🎉 FINALIZAÇÃO
# ============================================================
echo -e "\n${GREEN}${BOLD}✅ Deploy concluído com sucesso!${RESET}"
echo -e "${CYAN}API rodando em:${RESET} http://${IP}:8080"
echo -e "${CYAN}Bucket S3:${RESET} s3://erp-auto-update"
echo -e "${CYAN}Cliente salvo em:${RESET} client_simulator.py"
echo -e "\n🎉 O sistema ERP Auto Update está pronto para uso!\n"


