import cloudinary
import cloudinary.uploader
import os
from typing import Optional

def init_cloudinary():
    """Inicializa configuração do Cloudinary usando variáveis de ambiente"""
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

def upload_file(file_path: str, resource_type: str = "auto") -> Optional[str]:
    """
    Faz upload de um arquivo para o Cloudinary e retorna a URL segura.
    
    Args:
        file_path: Caminho do arquivo local
        resource_type: Tipo do arquivo ("auto", "image", "raw" para PDF/CSV)
    
    Returns:
        str: URL do arquivo no Cloudinary ou None em caso de erro
    """
    try:
        # Tenta inicializar caso não tenha sido feito ainda
        init_cloudinary()
        
        # Upload usando upload_large para suportar arquivos > 10MB
        response = cloudinary.uploader.upload_large(
            file_path,
            resource_type=resource_type,
            folder="biodiagnostico_uploads",
            chunk_size=6000000  # 6MB chunks
        )
        
        return response.get("secure_url")
        
    except Exception as e:
        print(f"Erro no upload para Cloudinary: {str(e)}")
        return None
