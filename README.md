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
      


# 2. ESTRUTURA DO PROJETO


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

Sempre teste em ambiente de staging antes de liberar novas versões.

# 8. Próximos Passos

Hospedar a API FastAPI na AWS EC2

Armazenar os pacotes .zip no bucket S3

Validar atualizações simultâneas em múltiplos terminais

Implementar rollback automático em caso de falha

Adicionar verificação de integridade dos arquivos

Configurar monitoramento e alertas com AWS CloudWatch

# 9. Fluxo do Sistema (Diagrama)
flowchart TD

A[Cliente ERP (Vnd.exe)] -->|Inicia e chama| B[client_simulator.exe]
B --> C[Ler versão atual (version.txt)]
C --> D[Verificar atualização na API /check_update]
D -->|Nova versão disponível| E[Baixar arquivo .zip do S3]
E --> F[Extrair e substituir arquivos em C:\piracaiasoft\bin]
F --> G[Atualizar version.txt]
G --> H[Iniciar ERP atualizado (Vnd.exe)]
D -->|Sem atualização| H

# 10. Autor

Desenvolvido por: Renato Junior Mathias
E-mail: renatojrmathias94@gmail.com

LinkedIn: linkedin.com/in/renato-jr-mathias-b76117221

# 11. Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais informações.
