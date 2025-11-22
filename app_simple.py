# =============================================================================
#  🌟 Détecteur de Poubelles - Version Professionnelle & Optimisée
# =============================================================================

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
import time

# =============================================================================
# 🌈 CONFIGURATION DE LA PAGE
# =============================================================================
st.set_page_config(
    page_title="Détecteur de Poubelles • IA",
    page_icon="🗑️",
    layout="centered"
)

# =============================================================================
# 🎨 STYLE PREMIUM (Glassmorphism + Animations)
# =============================================================================
st.markdown("""
<style>
    body {
        background: linear-gradient(145deg, #e3f2fd, #f8f9fa);
    }

    .main {
        background: transparent;
    }

    /* TITRE */
    .title-container {
        text-align: center;
        padding: 20px;
    }

    h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #0d6efd, #6610f2);
        -webkit-background-clip: text;
        color: transparent;
    }

    /* RESULT BOX */
    .result-box {
        font-size: 4rem;
        text-align: center;
        padding: 3rem 2rem;
        border-radius: 25px;
        margin: 2rem 0;
        font-weight: bold;
        backdrop-filter: blur(20px);
        background: rgba(255,255,255,0.45);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }

    .pleine {
        background: linear-gradient(135deg, #ff6b6bdd, #e63946dd);
        color: white;
    }

    .vide {
        background: linear-gradient(135deg, #51cf66dd, #2b8a3edd);
        color: white;
    }

    .aucune {
        background: linear-gradient(135deg, #ffc107dd, #ffcd39dd);
        color: #000;
    }

    /* CONFIDENCE TEXT */
    .confidence {
        font-size: 1.6rem;
        margin-top: 1rem;
        opacity: 0.85;
    }

    /* UPLOAD */
    .uploaded-img {
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }

</style>
""", unsafe_allow_html=True)

# =============================================================================
# 🏷️ HEADER
# =============================================================================
st.markdown("<div class='title-container'><h1>🗑️ Détecteur de Poubelles</h1></div>", unsafe_allow_html=True)
st.markdown("### 🌐 IA de classification : **Poubelle PLEINE ou VIDE**")
st.markdown("---")


# =============================================================================
# ⚙️ PARAMÈTRES AVANCÉS
# =============================================================================
with st.expander("⚙️ Paramètres avancés", expanded=False):
    seuil_conf = st.slider("Seuil de confiance minimum", 0.1, 0.95, 0.25, 0.05)
    st.info(f"🔧 Seuil actuel : **{seuil_conf:.0%}**")


# =============================================================================
# 🤖 CHARGEMENT DU MODÈLE YOLO
# =============================================================================
@st.cache_resource
def charger_modele():
    chemins = [
        "best.pt",
        "runs/detect/train/weights/best.pt",
        "runs/detect/train2/weights/best.pt",
        "runs/detect/train3/weights/best.pt"
    ]
    
    for chemin in chemins:
        if Path(chemin).exists():
            return YOLO(chemin)

    st.error("❌ Aucun modèle trouvé !")
    st.stop()


with st.spinner("⚙️ Chargement du modèle IA..."):
    modele = charger_modele()
st.success("💡 Modèle YOLOv9 chargé avec succès !")


# =============================================================================
# 🧠 FONCTION DE CLASSIFICATION
# =============================================================================
def classifier(image_path, model, seuil=0.25):
    results = model(image_path, conf=seuil, verbose=False)
    
    # Aucune détection ?
    if len(results[0].boxes) == 0:
        return {
            "statut": "AUCUNE DÉTECTION",
            "classe_css": "aucune",
            "emoji": "❌",
            "confiance": 0.0,
            "nom_classe": "Aucune",
            "nb_detections": 0
        }, results[0]

    # Détection principale
    boxes = results[0].boxes
    idx = boxes.conf.argmax()
    best_box = boxes[idx]

    classe_id = int(best_box.cls[0])
    confiance = float(best_box.conf[0])
    nom = results[0].names[classe_id].lower()

    if "pleine" in nom or "full" in nom:
        statut, css, emoji = "PLEINE", "pleine", "🔴"
    elif "vide" in nom or "empty" in nom:
        statut, css, emoji = "VIDE", "vide", "🟢"
    else:
        statut, css, emoji = "INCONNU", "aucune", "❓"

    return {
        "statut": statut,
        "classe_css": css,
        "emoji": emoji,
        "confiance": confiance,
        "nom_classe": results[0].names[classe_id],
        "nb_detections": len(boxes)
    }, results[0]


# =============================================================================
# 📤 UPLOAD IMAGE
# =============================================================================
st.markdown("### 📤 Importer une photo")
fichier = st.file_uploader(
    "Choisir une image",
    type=['jpg', 'jpeg', 'png'],
    label_visibility="collapsed"
)

# =============================================================================
# 🎯 TRAITEMENT
# =============================================================================
if fichier:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(fichier.getvalue())
        image_temp = tmp.name
    
    try:
        # Affichage
        st.markdown("<div class='uploaded-img'>", unsafe_allow_html=True)
        st.image(Image.open(fichier), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        # Inference
        with st.spinner("🔍 Analyse de l’image..."):
            start = time.time()
            resultat, prediction = classifier(image_temp, modele, seuil_conf)
            duration = time.time() - start

        # Résultat principal
        st.markdown(f"""
        <div class='result-box {resultat['classe_css']}'>
            {resultat['emoji']}<br>
            {resultat['statut']}
            <div class='confidence'>
                Confiance : {resultat['confiance']*100:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Métriques
        c1, c2, c3 = st.columns(3)
        c1.metric("Confiance", f"{resultat['confiance']*100:.1f}%")
        c2.metric("Temps", f"{duration:.2f}s")
        c3.metric("Détections", resultat['nb_detections'])

        # Image annotée
        if resultat['nb_detections'] > 0:
            st.markdown("---")
            st.markdown("### 🎯 Visualisation des détections")
            img = prediction.plot()
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            st.image(img_rgb, use_container_width=True)

        # Infos
        with st.expander("📄 Détails de l'analyse"):
            st.write(resultat)

    finally:
        os.unlink(image_temp)

else:
    st.info("""
    ### 👋 Bienvenue dans votre détecteur de poubelles intelligent !

    **Utilisation :**
    - 📤 Importer une photo
    - 🤖 L’IA analyse
    - 📊 Résultat affiché en quelques secondes

    **Conseils :**
    - Photo bien éclairée
    - Poubelle visible entièrement
    - Vue de face de préférence
    """)


# =============================================================================
# 🏁 FOOTER
# =============================================================================
st.markdown("---")
st.caption("✨ Développé avec YOLOv9 • Streamlit • Ultralytics")
