import requests

url = "http://localhost:8080/check_update"
terminal_version = "0.9.0"

print(f"Terminal 1 com versão {terminal_version} verificando atualização...")
r = requests.get(url, params={"version": terminal_version})

print("Status code:", r.status_code)
print("Resposta bruta:", r.text)  # <--- Veja o que realmente vem da API

try:
    data = r.json()
    print("Resposta JSON:", data)
except Exception as e:
    print("Erro ao decodificar JSON:", e)



import requests
import os
import zipfile

# --- Configurações ---
SERVER_URL = "http://localhost:8080"
LOCAL_VERSION_FILE = "client_version.txt"
UPDATE_FOLDER = "update_files"

# --- Função para ler a versão local ---
def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    return "0.0.0"  # versão inicial padrão

# --- Função para salvar nova versão ---
def save_local_version(version):
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(version)

# --- Verificar atualização ---
def check_for_update():
    local_version = get_local_version()
    print(f"Terminal com versão {local_version} verificando atualização...")

    try:
        resp = requests.get(f"{SERVER_URL}/check_update", params={"version": local_version})
        print("Status code:", resp.status_code)
        print("Resposta bruta:", resp.text)
        data = resp.json()

        if data.get("update_available"):
            print(f"⚙️ Nova versão disponível: {data['latest_version']}")
            download_update(data["url"], data["latest_version"])
        else:
            print("✅ Nenhuma atualização disponível.")
    except Exception as e:
        print("Erro ao verificar atualização:", e)

# --- Baixar e aplicar atualização ---
def download_update(url, version):
    os.makedirs(UPDATE_FOLDER, exist_ok=True)
    local_zip_path = os.path.join(UPDATE_FOLDER, f"{version}.zip")

    print(f"⬇️ Baixando atualização: {url}")
    resp = requests.get(url)

    if resp.status_code == 200:
        with open(local_zip_path, "wb") as f:
            f.write(resp.content)
        print("✅ Download concluído:", local_zip_path)

        # Simular instalação
        apply_update(local_zip_path, version)
    else:
        print("❌ Falha ao baixar o arquivo:", resp.status_code)

# --- Aplicar atualização (simulação) ---
def apply_update(zip_path, version):
    print(f"📦 Aplicando atualização para versão {version}...")
    extract_dir = "installed_version"
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Atualiza versão local
    save_local_version(version)
    print(f"✅ Atualização concluída! Nova versão instalada: {version}")

# --- Execução principal ---
if __name__ == "__main__":
    check_for_update()
