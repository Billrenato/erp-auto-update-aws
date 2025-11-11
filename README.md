# ERP Auto Update System

Sistema de atualização automática para terminais ERP, desenvolvido em Python 3.11 e preparado para rodar via AWS (EC2 + S3).

O projeto permite que múltiplos terminais atualizem automaticamente seus executáveis (.exe) e 
arquivos auxiliares através de uma API centralizada, garantindo distribuição eficiente e controle de versões.


# 1. VISÃO GERAL


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


# 3. TECNOLOGIAS


- Python 3.11
- FastAPI ou Flask (para a API)
- Requests, ZipFile, io
- AWS S3 (armazenamento das versões)
- AWS EC2 (execução da API)
- PyInstaller (geração do executável .exe)
- Docker (empacotamento e deploy automatizado)


# 4. CONFIGURAÇÃO DO CLIENTE


1. Configure o diretório de instalação no código:
   INSTALL_DIR = r"C:\sistema\bin"

2. Gere o executável:
   pyinstaller --onefile client_simulator.py

3. Copie o executável gerado para os terminais que farão a atualização automática.


#5. Deploy na AWS
1. Criar o bucket S3

Nome sugerido: erp-auto-update-files

Estrutura:

versions/
  ├── v1.0.1.zip
  ├── v1.0.2.zip
  └── manifest.json

2. Subir a API para o EC2
docker build -t erp-update-server ./api
docker run -d -p 8080:8000 erp-update-server

3. Endpoints Disponíveis

/check_update?version=1.0.0 → Verifica nova versão

/download/v1.0.1.zip → Baixa a nova versão

/upload_update → Envia nova versão (via formulário)

# 6. Teste Local
Rodar o servidor
python api/main.py

Executar o cliente simulador
python client_simulator.py

# 7. Segurança e Boas Práticas

Utilize hash MD5 ou SHA256 para validar a integridade dos arquivos ZIP.

Configure HTTPS via Nginx ou AWS CloudFront.

Restrinja permissões de gravação no diretório de instalação (C:\piracaiasoft\bin).

Armazene chaves e tokens AWS em variáveis de ambiente.

Gere logs detalhados de atualização (update.log) para auditoria.

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

# ERP Auto Update - Deploy de Teste na AWS

Este repositório contém o sistema de atualização automática para terminais ERP, rodando em AWS EC2 e usando S3 para hospedar os arquivos de atualização.


# Fluxo de atualização

- O terminal ERP (client_simulator.py) lê a versão local (version.txt).

- Consulta a API FastAPI hospedada na EC2:

- GET http://<EC2_PUBLIC_IP>:8080/check_update?version=<versao_atual>


- A API verifica o manifest.json no S3:

- Se houver nova versão disponível, retorna a URL do .zip.

- O terminal baixa o .zip e extrai os arquivos na pasta de instalação.

- Atualiza o version.txt para a nova versão.

- Inicia o sistema ERP atualizado automaticamente.

# ⚙ Configuração AWS

- EC2 Instance

- Tipo: t3.micro

- Sistema: Ubuntu 22.04

- Docker + Docker Compose instalados

- S3 Bucket

- Nome: erp-auto-update

- Região: sa-east-1 (São Paulo)

- Bucket policy configurada para permitir leitura pública de objetos.

- AWS CLI

- Configurada com usuário principal com permissão de S3.

# Upload de arquivos de atualização:

aws s3 cp v1.0.6.zip s3://erp-auto-update/v1.0.6.zip
aws s3 cp manifest.json s3://erp-auto-update/manifest.json

# 🐳 Rodando a API no Docker

Build e start:

sudo docker compose up -d


Verificar containers rodando:

sudo docker ps


API disponível em:

http://<EC2_PUBLIC_IP>:8080



# Log do Teste:

Terminal com versão 0.0.0 verificando atualizações...
Nova versão 1.0.6 disponível! Iniciando atualização...
Baixando atualização de https://erp-auto-update.s3.sa-east-1.amazonaws.com/v1.0.6.zip ...
Atualização extraída com sucesso!
Terminal atualizado para a versão 1.0.6
Iniciando o sistema ERP atualizado...