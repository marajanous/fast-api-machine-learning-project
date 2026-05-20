import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config.database import db, minio_client
from botocore.exceptions import ClientError

router = APIRouter(prefix="/datasets", tags=["Datasets"])
logger = logging.getLogger(__name__)

BUCKET_NAME = "mlops-datasets"

def ensure_bucket_exists():
    """Funkce, která zajistí, že cílový bucket v MinIO existuje."""
    try:
        minio_client.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        try:
            minio_client.create_bucket(Bucket=BUCKET_NAME)
            logger.info(f"Vytvořen nový bucket v MinIO: {BUCKET_NAME}")
        except Exception as e:
            logger.error(f"Nepodařilo se vytvořit bucket v MinIO: {e}")

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(file: UploadFile = File(...)):
    """Nahrání CSV souboru do MinIO a zápis metadat do MongoDB."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Povoleny jsou pouze .csv soubory"
        )
    
    # Ujistíme se, že bucket existuje
    ensure_bucket_exists()
    
    try:
        # NAHRÁNÍ SOUBORU DO MINIO
        logger.info(f"Nahrávám soubor {file.filename} do MinIO...")
        minio_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file.filename
        )
        
        # ZÁPIS METADAT DO MONGODB
        logger.info(f"Ukládám metadata souboru {file.filename} do MongoDB...")
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": file.size,
            "status": "uploaded"
        }
        await db["datasets"].insert_one(metadata)
        
        return {
            "status": "success",
            "message": "Dataset byl úspěšně uložen do MinIO i MongoDB!",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Chyba při ukládání datasetu: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Chyba na serveru při nahrávání: {str(e)}"
        )

@router.get("/download/{filename}")
async def get_dataset_download_url(filename: str):
    """Vygeneruje dočasný bezpečný odkaz (presigned URL) pro stažení souboru z MinIO."""
    logger.info(f"Požadavek na stažení souboru: {filename}")
    
    # Ověření v MongoDB, zda soubor v systému evidujeme
    file_metadata = await db["datasets"].find_one({"filename": filename})
    if not file_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dataset nebyl v databázi nalezen"
        )
    
    try:
        # Vygenerování presigned URL z MinIO
        logger.info(f"Generuji presigned URL z MinIO pro: {filename}")
        presigned_url = minio_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=600
        )
        
        # Úprava adresy z interní Docker sítě (minio) na lokální počítač 
        local_presigned_url = presigned_url.replace("http://minio:9000", "http://localhost:9000")
        
        return {
            "status": "success",
            "filename": filename,
            "download_url": local_presigned_url,
            "expires_in_seconds": 600
        }
        
    except Exception as e:
        logger.error(f"Chyba při generování presigned URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Nepodařilo se vygenerovat odkaz ke stažení"
        )

@router.delete("/{filename}")
async def remove_dataset(filename: str):
    """Smazání datasetu z MinIO i z MongoDB."""
    logger.info(f"Požadavek na odstranění datasetu: {filename}")
    
    # Odstranění z MinIO úložiště
    try:
        minio_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        logger.info(f"Soubor {filename} smazán z MinIO.")
    except Exception as e:
        logger.warning(f"Nepodařilo se smazat soubor z MinIO (možná již neexistoval): {e}")
        
    # Odstranění metadat z MongoDB
    result = await db["datasets"].delete_one({"filename": filename})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dataset nebyl v databázi nalezen"
        )
        
    return {
        "status": "success",
        "message": f"Dataset {filename} byl úspěšně odstraněn z MinIO i MongoDB"
    }