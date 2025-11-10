# ERP Auto Update System

Sistema de atualização automática para terminais ERP, desenvolvido em Python 3.11 e preparado para rodar via AWS (EC2 + S3).

O projeto permite que múltiplos terminais atualizem automaticamente seus executáveis (.exe) e arquivos auxiliares através de uma API centralizada, garantindo distribuição eficiente e controle de versões.

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


                   ┌──────────────────────────┐
                   │        Usuário           │
                   │ (Terminal / Máquina ERP) │
                   └────────────┬─────────────┘
                                │
                                │ Verifica Atualizações
                                ▼
                     ┌──────────────────────────┐
                     │   API de Atualização     │
                     │ (Python + FastAPI)       │
                     │       Porta 8080         │
                     └────────────┬─────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
     ┌─────────────────────┐            ┌──────────────────────────┐
     │ Endpoint/check_update│           │ Endpoint /download/{zip} │
     │ Retorna JSON com:   │            │ Fornece arquivo .zip com │
     │ - Versão atual      │            │ novos binários(até 500MB)│
     │ - URL de download   │            └──────────────────────────┘
     │ - Flag de update    │
     └─────────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │        AWS S3 Bucket     │
                   │  (armazenamento dos ZIPs)│
                   └────────────┬─────────────┘
                                │
                                ▼
                     ┌──────────────────────────┐
                     │   Cliente Python (EXE)   │
                     │ client_simulator.exe     │
                     │--------------------------│
                     │ 1. Verifica versão local │
                     │ 2. Consulta API          │
                     │ 3. Baixa atualização ZIP │
                     │ 4. Extrai e substitui    │
                     │ 5. Inicia Vnd.exe        │
                     └──────────────────────────┘



===============================================================================
2. ESTRUTURA DO PROJETO
===============================================================================

erp-auto-update-aws/
│
├── server/
│   ├── app.py                 # API principal (FastAPI/Flask)
│   ├── versions/              # Versões disponíveis
│   └── requirements.txt       # Dependências do servidor
│
├── client/
│   ├── client_simulator.py    # Cliente Python
│   ├── version.txt            # Versão atual instalada
│   └── build/                 # Executável gerado pelo PyInstaller
│
├── Dockerfile                 # Configuração de build e deploy
├── docker-compose.yml         # Configuração de container (opcional)
└── README.md                  # Este arquivo

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

