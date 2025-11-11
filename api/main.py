from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import boto3, json, os
from botocore.exceptions import ClientError

app = FastAPI(title="ERP Auto Update API")

# Nome do bucket e região — variáveis de ambiente
S3_BUCKET = os.getenv("S3_BUCKET", "erp-auto-update")
REGION = os.getenv("AWS_REGION", "sa-east-1")

# Inicializa cliente S3
s3 = boto3.client("s3", region_name=REGION)

# --------------------------------------------------------
# 1️⃣ Verificar se há nova versão
# --------------------------------------------------------
@app.get("/check_update")
def check_update(version: str):
    """Verifica se há uma nova versão no S3."""
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key="manifest.json")
        manifest = json.loads(obj["Body"].read().decode("utf-8"))
    except ClientError as e:
        return JSONResponse(
            {"error": f"Manifesto não encontrado: {str(e)}"},
            status_code=404
        )

    latest = manifest.get("version")
    file_name = manifest.get("file")

    if latest and latest != version:
        file_url = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{file_name}"
        return {
            "update_available": True,
            "latest_version": latest,
            "url": file_url
        }

    return {"update_available": False}


# --------------------------------------------------------
# 2️⃣ Fazer upload de nova versão
# --------------------------------------------------------
@app.post("/upload_update")
async def upload_update(file: UploadFile, version: str = Form(...)):
    """Faz upload de nova versão e atualiza manifest.json no S3."""
    file_name = f"erp_update_v{version}.zip"

    try:
        # Envia o arquivo ZIP
        s3.upload_fileobj(
            file.file,
            S3_BUCKET,
            file_name,
            ExtraArgs={"ContentType": "application/zip"}
        )
    except Exception as e:
        return JSONResponse({"error": f"Falha ao enviar para o S3: {str(e)}"}, status_code=500)

    # Atualiza o manifest.json
    manifest_data = {
        "update": True,
        "version": version,
        "file": file_name
    }

    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key="manifest.json",
            Body=json.dumps(manifest_data, indent=2),
            ContentType="application/json"
        )
    except Exception as e:
        return JSONResponse({"error": f"Falha ao atualizar manifest: {str(e)}"}, status_code=500)

    return {"status": "Nova versão publicada", "version": version}
