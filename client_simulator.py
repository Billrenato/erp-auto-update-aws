import requests
import os
import zipfile
import io
import time

# -------------------------------------------------
# Configurações fixas do cliente (ALTERE SOMENTE AQUI)
# -------------------------------------------------
API_URL = "http://0.0.0.0:8080/check_update"
DOWNLOAD_BASE = "https://erp-auto-update.s3.sa-east-1.amazonaws.com/"
INSTALL_DIR = r"C:\ERP_Auto_Update_Client"
VERSION_FILE = os.path.join(INSTALL_DIR, "version.txt")

# -------------------------------------------------
# Funções utilitárias
# -------------------------------------------------
def get_local_version():
    """Lê a versão atual instalada no terminal"""
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()

def set_local_version(version):
    """Atualiza o arquivo version.txt"""
    with open(VERSION_FILE, "w") as f:
        f.write(version)

def ensure_install_dir():
    """Garante que a pasta de instalação existe"""
    os.makedirs(INSTALL_DIR, exist_ok=True)

def download_and_extract(url, target_dir):
    """Baixa o ZIP e extrai na pasta alvo"""
    print(f" Baixando atualização de {url} ...")
    r = requests.get(url)
    if r.status_code != 200:
        print("Falha no download:", r.status_code)
        return False

    with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
        zip_ref.extractall(target_dir)
    print(" Atualização extraída com sucesso!")
    return True

# -------------------------------------------------
# Fluxo principal
# -------------------------------------------------
def main():
    ensure_install_dir()
    current_version = get_local_version()

    print(f"Terminal com versão {current_version} verificando atualizações...")
    try:
        r = requests.get(API_URL, params={"version": current_version}, timeout=10)
    except requests.exceptions.RequestException as e:
        print("Erro ao conectar ao servidor:", e)
        return

    if r.status_code != 200:
        print("Erro HTTP:", r.status_code)
        return

    data = r.json()
    if data.get("update_available"):
        latest = data["latest_version"]
        url = data["url"]
        print(f"Nova versão {latest} disponível! Iniciando atualização...")

        if download_and_extract(url, INSTALL_DIR):
            set_local_version(latest)
            print(f"Terminal atualizado para a versão {latest}")
    else:
        print("Nenhuma atualização disponível.")

    time.sleep(2)

    # -------------------------------------------------
    # Após verificar ou atualizar, inicia o sistema Delphi
    # -------------------------------------------------
    erp_exe = os.path.join(INSTALL_DIR, "Vnd.exe")

    if os.path.exists(erp_exe):
        print("▶Iniciando o sistema ERP atualizado...")
        os.startfile(erp_exe)
    else:
        print("Arquivo ERP não encontrado:", erp_exe)

if __name__ == "__main__":
    main()
