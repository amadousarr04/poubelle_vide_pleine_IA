"""
🗑️ Backend FastAPI - Détecteur de Poubelles
API de classification PLEINE/VIDE avec YOLOv9
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from ultralytics import YOLO
from PIL import Image
import io
import os
from pathlib import Path
import time
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(
    title="🗑️ Détecteur de Poubelles API",
    description="Classification intelligente de poubelles (PLEINE/VIDE) avec YOLOv9",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# CORS - Autoriser toutes les origines pour le frontend
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production: spécifier l'URL exacte du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CHARGEMENT DU MODÈLE YOLO
# ============================================================================
MODEL_PATHS = [
    Path("best.pt"),
    Path("../best.pt"),
    Path("../../best.pt"),
    Path("../../../best.pt"),
]

model = None
MODEL_PATH = None

for path in MODEL_PATHS:
    if path.exists():
        MODEL_PATH = path
        try:
            model = YOLO(str(path))
            logger.info(f"✅ Modèle chargé depuis: {path.absolute()}")
            break
        except Exception as e:
            logger.error(f"❌ Erreur chargement {path}: {e}")

if model is None:
    logger.error("❌ ERREUR CRITIQUE: Aucun modèle best.pt trouvé!")
    raise FileNotFoundError("Le fichier best.pt est requis. Placez-le dans le dossier backend/")

# ============================================================================
# ENDPOINTS API
# ============================================================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "application": "🗑️ Détecteur de Poubelles",
        "version": "1.0.0",
        "status": "✅ Opérationnelle",
        "modele": "YOLOv9",
        "endpoints": {
            "health": "/health - Vérification état serveur",
            "predict": "/predict - Classification d'image (POST)",
            "info": "/model-info - Informations sur le modèle",
            "docs": "/docs - Documentation interactive"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de santé pour vérifier que l'API fonctionne"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH.absolute()) if MODEL_PATH else None,
        "timestamp": time.time()
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Classification d'une image de poubelle
    
    Args:
        file: Image (JPG, PNG, JPEG)
    
    Returns:
        JSON avec résultat de classification
    """
    
    # Validation du type de fichier
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image (JPG, PNG, JPEG)"
        )
    
    try:
        # Lecture de l'image
        start_time = time.time()
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Conversion en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        logger.info(f"📸 Analyse de: {file.filename} ({image.size})")
        
        # Prédiction avec le modèle
        results = model(image, conf=0.25, verbose=False)
        processing_time = time.time() - start_time
        
        # Traitement des résultats
        if len(results[0].boxes) > 0:
            boxes = results[0].boxes
            best_idx = boxes.conf.argmax()
            best_box = boxes[best_idx]
            
            class_id = int(best_box.cls[0])
            confidence = float(best_box.conf[0])
            class_name = results[0].names[class_id]
            
            # Détermination du statut
            if "pleine" in class_name.lower() or "full" in class_name.lower():
                status = "PLEINE"
                emoji = "🔴"
                color = "#ef4444"
                message = "⚠️ Collecte requise immédiatement!"
                priority = "HAUTE"
            elif "vide" in class_name.lower() or "empty" in class_name.lower():
                status = "VIDE"
                emoji = "🟢"
                color = "#10b981"
                message = "✅ Aucune action nécessaire"
                priority = "BASSE"
            else:
                status = "INCONNU"
                emoji = "🟡"
                color = "#f59e0b"
                message = "🔍 Vérification manuelle recommandée"
                priority = "MOYENNE"
            
            # Bounding box
            bbox = best_box.xyxy[0].cpu().numpy().tolist()
            
            response = {
                "success": True,
                "status": status,
                "emoji": emoji,
                "color": color,
                "message": message,
                "priority": priority,
                "confidence": round(confidence, 4),
                "confidence_percent": round(confidence * 100, 2),
                "class_name": class_name,
                "class_id": class_id,
                "num_detections": len(boxes),
                "bbox": {
                    "x1": round(bbox[0], 2),
                    "y1": round(bbox[1], 2),
                    "x2": round(bbox[2], 2),
                    "y2": round(bbox[3], 2)
                },
                "processing_time": round(processing_time, 3),
                "image_info": {
                    "width": image.width,
                    "height": image.height,
                    "format": str(image.format) if image.format else "Unknown",
                    "filename": file.filename
                }
            }
            
            logger.info(f"✅ Résultat: {status} ({confidence*100:.1f}%)")
        
        else:
            # Aucune détection
            response = {
                "success": True,
                "status": "AUCUNE_DETECTION",
                "emoji": "❌",
                "color": "#6b7280",
                "message": "Aucune poubelle détectée dans l'image",
                "priority": "N/A",
                "confidence": 0.0,
                "confidence_percent": 0.0,
                "class_name": None,
                "class_id": -1,
                "num_detections": 0,
                "bbox": None,
                "processing_time": round(processing_time, 3),
                "image_info": {
                    "width": image.width,
                    "height": image.height,
                    "format": str(image.format) if image.format else "Unknown",
                    "filename": file.filename
                }
            }
            
            logger.warning("⚠️ Aucune poubelle détectée")
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )

@app.get("/model-info")
async def model_info():
    """Informations détaillées sur le modèle"""
    if model is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé")
    
    return {
        "model_type": "YOLOv9",
        "model_path": str(MODEL_PATH.absolute()) if MODEL_PATH else None,
        "classes": model.names if model else {},
        "num_classes": len(model.names) if model else 0,
        "class_list": list(model.names.values()) if model else [],
        "input_size": 640,
        "framework": "Ultralytics"
    }

@app.get("/download-model")
async def download_model():
    """
    Télécharger le fichier du modèle YOLOv9
    """
    try:
        if MODEL_PATH is None or not MODEL_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail="Fichier du modèle non trouvé"
            )
        
        logger.info(f"📥 Téléchargement du modèle: {MODEL_PATH}")
        
        return FileResponse(
            path=str(MODEL_PATH),
            filename="best.pt",
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=best.pt"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du téléchargement: {str(e)}"
        )

# ============================================================================
# DÉMARRAGE DU SERVEUR
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Démarrage du serveur sur le port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
