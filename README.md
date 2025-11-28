#  ERP Auto Update System

Sistema robusto de atualização automática para terminais ERP, desenvolvido em **Python 3.11** e otimizado para **AWS** (EC2 + S3).

Este projeto garante a distribuição eficiente e centralizada de novos executáveis (`.exe`) e arquivos auxiliares para múltiplos terminais, utilizando uma **API centralizada** para gerenciamento e controle de versões.

---

##  1. Visão Geral do Fluxo de Atualização

O sistema opera com uma arquitetura Cliente-Servidor simples e eficaz para gerenciar o ciclo de vida das atualizações.

### **Cliente (Terminal ERP - Python/Executável)**

1.  **Verificação:** Lê a versão atual instalada (`version.txt`).
2.  **Consulta:** Comunica-se com a API de atualização para verificar a disponibilidade de uma versão mais recente.
3.  **Download:** Faz o download do arquivo `.zip` da nova versão (hospedado no S3).
4.  **Extração:** Extrai automaticamente o conteúdo para o diretório de instalação configurado (Ex: `C:\sistema\bin`).
5.  **Finalização:** Atualiza o `version.txt` com o novo número de versão e inicia o ERP (`Vnd.exe`) atualizado.

### **Servidor (API Centralizada - Python + FastAPI/Flask)**

* **Tecnologia:** Desenvolvido com **FastAPI** (ou Flask) e empacotado via **Docker**.
* **Hospedagem:** Executado em uma instância **AWS EC2** (via Docker + Gunicorn/Uvicorn).
* **Armazenamento:** Arquivos de versão (`.zip` e `manifest.json`) hospedados no **AWS S3 Bucket**.
* **Endpoints Principais:**
    * `/check_update`: Informa ao cliente se há uma nova versão disponível.
    * `/download/{arquivo}`: Fornece o `.zip` da versão solicitada (com redirecionamento para o S3).

---

##  2. Estrutura do Projeto

A organização do repositório é focada em separar a lógica da API, o armazenamento e os utilitários do cliente.

---
      erp-auto-update-aws/
      ├── api/
      │   ├── Dockerfile             # Configuração de build para o container da API
      │   ├── main.py                # Lógica principal da API (FastAPI/Flask)
      │   └── requirements.txt       # Dependências do servidor
      │
      ├── client/
      │   └── client_simulator.py    # Script que simula o terminal cliente de atualização
      │
      ├── storage/                   # Arquivos de exemplo (que serão movidos para o S3)
      │   ├── manifest.json          # JSON com a versão mais recente e hashes
      │   └── v1.0.5.zip             # Arquivo de atualização (ficará no S3)
      │
      └── docker-compose.yml         # Configuração de container para desenvolvimento local
---

---

##  3. Tecnologias Utilizadas

| Categoria | Tecnologia | Uso Principal |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.11 | Desenvolvimento do Cliente e Servidor |
| **Servidor/API** | FastAPI / Flask | Criação dos Endpoints RESTful |
| **Infraestrutura** | AWS S3, AWS EC2 | Armazenamento de arquivos, Hospedagem da API |
| **Empacotamento** | PyInstaller | Geração do executável (`.exe`) do cliente |
| **Deploy** | Docker, Docker Compose | Empacotamento, orquestração e deploy automatizado |
| **Bibliotecas** | Requests, ZipFile, io | Operações HTTP e manipulação de ZIP |

---

##  4. Configuração e Execução do Cliente

Para que o terminal realize a atualização, siga estes passos:

1.  **Defina o Diretório:** No arquivo `client_simulator.py`, configure o caminho de instalação:
    ```python
    INSTALL_DIR = r"C:\sistema\bin"
    ```
2.  **Gere o Executável:** Utilize o PyInstaller para criar o binário standalone:
    ```bash
    pyinstaller --onefile client_simulator.py
    ```
3.  **Distribuição:** Copie o executável gerado para os terminais onde a atualização será executada.

### **Teste Local**

1.  **Rodar o Servidor:**
    ```bash
    python api/main.py
    ```
2.  **Executar o Cliente Simulado:**
    ```bash
    python client_simulator.py
    ```

---

## ☁️ 5. Deploy na AWS e Endpoints

### **5.1. Configuração do S3**

1.  Crie o Bucket S3 (Ex: `erp-auto-update-files`).
2.  **Estrutura Recomendada:**
    ```
    versions/
    ├── manifest.json
    ├── v1.0.1.zip
    └── v1.0.2.zip
    ```
3.  **Upload de Arquivos de Versão:** Utilize o AWS CLI:
    ```bash
    aws s3 cp v1.0.6.zip s3://erp-auto-update-files/versions/v1.0.6.zip
    aws s3 cp manifest.json s3://erp-auto-update-files/versions/manifest.json
    ```

### **5.2. Deploy da API no EC2 (Docker)**

1.  Construa a imagem Docker:
    ```bash
    docker build -t erp-update-server ./api
    ```
2.  Execute o container:
    ```bash
    docker run -d -p 8080:8000 erp-update-server
    ```
    *(A porta 8080 é exposta publicamente e mapeada para a porta 8000 do container.)*

### **5.3. Endpoints Disponíveis**

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **GET** | `/check_update?version=1.0.0` | Verifica se há uma versão mais recente que a informada. |
| **GET** | `/download/v1.0.1.zip` | Retorna o arquivo de atualização solicitado. |
| **POST** | `/upload_update` | Endpoint opcional para envio (upload) de novas versões (via formulário). |

---

##  6. Segurança e Boas Práticas

Para garantir a integridade e segurança do sistema:

* **Integridade do Arquivo:** Utilize **hash MD5** ou **SHA256** no `manifest.json` para que o cliente valide a integridade do `.zip` após o download.
* **Criptografia:** Configure **HTTPS** na API, utilizando Nginx como reverse proxy ou o serviço **AWS CloudFront**.
* **Permissões:** Restrinja as permissões de gravação no diretório de instalação do cliente (Ex: `C:\sistema\bin`).
* **Credenciais:** Armazene chaves e tokens AWS de forma segura, utilizando **variáveis de ambiente** ou o **AWS Parameter Store/Secrets Manager**.
* **Auditoria:** Implemente um sistema de log detalhado (`update.log`) para auditoria de cada processo de atualização no terminal.

---

##  7. Próximos Passos (Roadmap)

1.  **Configuração Completa:** Finalizar a configuração e testes da API rodando na AWS EC2 e arquivos .zip hospedados no S3.
2.  **Validação:** Testar e validar o fluxo de atualização em um ambiente com múltiplos terminais.
3.  **Estabilidade:** Implementar o recurso de **rollback automático** em caso de falha na extração ou inicialização pós-atualização.
4.  **Verificação:** Adicionar checagem de integridade (hash) do executável do ERP após a atualização.
5.  **Monitoramento:** Configurar alertas e métricas de atualização via **AWS CloudWatch**.

---

## 📄 Log de Teste

Exemplo de saída de log no terminal cliente durante o processo de atualização:

---
       Terminal com versão 0.0.0 verificando atualizações...
       Nova versão 1.0.6 disponível! Iniciando atualização...
       Baixando atualização de https://erp-auto-update.s3.sa-east-1.amazonaws.com/v1.0.6.zip ...
       Atualização extraída com sucesso!
       Terminal atualizado para a versão 1.0.6
       Iniciando o sistema ERP atualizado...
      PS C:\erp-auto-update-aws> 
---
