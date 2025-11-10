from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
import os, json

app = FastAPI()
STORAGE_DIR = "/storage"

@app.get("/check_update")
def check_update(version: str):
    """Verifica se há uma nova versão disponível."""
    manifest_path = os.path.join(STORAGE_DIR, "manifest.json")

    if not os.path.exists(manifest_path):
        return JSONResponse({"error": "Manifesto não encontrado"}, status_code=404)

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    latest = manifest.get("version")
    file_name = manifest.get("file")

    if latest and latest != version:
        return {
            "update_available": True,
            "latest_version": latest,
            "url": f"http://localhost:8080/download/{file_name}"
        }

    return {"update_available": False}


@app.get("/download/{filename}")
def download_file(filename: str):
    """Permite o download de um arquivo de atualização."""
    file_path = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse({"error": "Arquivo não encontrado"}, status_code=404)


@app.post("/upload_update")
async def upload_update(file: UploadFile, version: str = Form(...)):
    """Faz upload de uma nova versão (simula o envio do .exe/.zip)."""
    # Caminho onde será salvo o arquivo
    file_name = f"erp_update_v{version}.zip"
    save_path = os.path.join(STORAGE_DIR, file_name)

    # Salva o arquivo enviado
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # Cria o novo manifest.json
    manifest_data = {
        "update": True,
        "version": version,
        "file": file_name
    }

    manifest_path = os.path.join(STORAGE_DIR, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)

    return {"status": "Nova versão publicada", "version": version}