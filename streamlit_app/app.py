"""
🗑️ Smart Bin Detector - Application Streamlit
Classification intelligente de poubelles avec YOLOv9
"""

import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from pathlib import Path

# ============================================================================
# CONFIGURATION PAGE
# ============================================================================
st.set_page_config(
    page_title="🗑️ Smart Bin Detector",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/amadousarr04/detection_poubelle',
        'Report a bug': "https://github.com/amadousarr04/detection_poubelle/issues",
        'About': "# Smart Bin Detector\nClassification intelligente de poubelles avec YOLOv9"
    }
)

# ============================================================================
# STYLES CSS PERSONNALISÉS
# ============================================================================
st.markdown("""
<style>
    /* Fond principal avec gradient animé */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        animation: gradientFlow 15s ease infinite;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Carte glassmorphisme */
    .stApp > header {
        background-color: transparent;
    }
    
    /* Titre principal */
    h1 {
        color: white;
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        animation: fadeInDown 1s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Cartes */
    .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: slideUp 0.8s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Métriques */
    .css-1xarl3l {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
    }
    
    /* Badge de statut */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
        }
        50% {
            box-shadow: 0 0 0 20px rgba(102, 126, 234, 0);
        }
    }
    
    .status-pleine {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .status-vide {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    /* Barre de progression personnalisée */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 12px 12px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALISATION SESSION STATE
# ============================================================================
if 'analyses_history' not in st.session_state:
    st.session_state.analyses_history = []
if 'total_analyses' not in st.session_state:
    st.session_state.total_analyses = 0
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'pleine': 0,
        'vide': 0,
        'total_confidence': 0,
        'total_time': 0
    }

# ============================================================================
# CHARGEMENT DU MODÈLE
# ============================================================================
@st.cache_resource
def load_model():
    """Charge le modèle YOLOv9 avec cache"""
    model_paths = [
        Path("best.pt"),
        Path("../best.pt"),
        Path("backend/best.pt"),
        Path("../backend/best.pt"),
    ]
    
    for path in model_paths:
        if path.exists():
            try:
                model = YOLO(str(path))
                return model, str(path.absolute())
            except Exception as e:
                continue
    
    return None, None

# ============================================================================
# FONCTION DE DÉTECTION
# ============================================================================
def detect_bin(image, model, confidence_threshold=0.25):
    """
    Effectue la détection sur une image
    """
    start_time = time.time()
    
    # Conversion PIL vers numpy
    img_array = np.array(image)
    
    # Prédiction
    results = model(img_array, conf=confidence_threshold, verbose=False)
    processing_time = time.time() - start_time
    
    result_data = {
        'timestamp': datetime.now(),
        'processing_time': processing_time,
        'image_size': image.size
    }
    
    if len(results[0].boxes) > 0:
        boxes = results[0].boxes
        best_idx = boxes.conf.argmax()
        best_box = boxes[best_idx]
        
        class_id = int(best_box.cls[0])
        confidence = float(best_box.conf[0])
        class_name = results[0].names[class_id]
        bbox = best_box.xyxy[0].cpu().numpy()
        
        # Détermination du statut
        if "pleine" in class_name.lower() or "full" in class_name.lower():
            status = "PLEINE"
            emoji = "🔴"
            color = "#ef4444"
            message = "⚠️ Collecte requise immédiatement!"
        elif "vide" in class_name.lower() or "empty" in class_name.lower():
            status = "VIDE"
            emoji = "🟢"
            color = "#10b981"
            message = "✅ Aucune action nécessaire"
        else:
            status = "INCONNU"
            emoji = "🟡"
            color = "#f59e0b"
            message = "🔍 Vérification manuelle recommandée"
        
        # Dessiner la bounding box
        img_with_box = img_array.copy()
        x1, y1, x2, y2 = bbox.astype(int)
        
        # Couleur selon status
        box_color = (239, 68, 68) if status == "PLEINE" else (16, 185, 129)
        
        cv2.rectangle(img_with_box, (x1, y1), (x2, y2), box_color, 3)
        
        # Label
        label = f"{status} {confidence*100:.1f}%"
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(img_with_box, (x1, y1 - label_h - 10), (x1 + label_w, y1), box_color, -1)
        cv2.putText(img_with_box, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        result_data.update({
            'status': status,
            'emoji': emoji,
            'color': color,
            'message': message,
            'confidence': confidence,
            'class_name': class_name,
            'bbox': bbox.tolist(),
            'image_with_detection': img_with_box,
            'num_detections': len(boxes)
        })
    else:
        result_data.update({
            'status': 'AUCUNE_DETECTION',
            'emoji': '❌',
            'color': '#6b7280',
            'message': 'Aucune poubelle détectée',
            'confidence': 0.0,
            'image_with_detection': img_array,
            'num_detections': 0
        })
    
    return result_data

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("## 🗑️ Smart Bin Detector")
    st.markdown("---")
    
    # Menu de navigation
    page = st.radio(
        "📋 Navigation",
        ["🏠 Accueil", "📊 Statistiques", "⚙️ Paramètres", "ℹ️ À propos"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Chargement du modèle
    with st.spinner("🔄 Chargement du modèle..."):
        model, model_path = load_model()
    
    if model:
        st.success("✅ Modèle chargé")
        st.caption(f"📁 {Path(model_path).name}")
    else:
        st.error("❌ Modèle non trouvé")
        st.stop()
    
    st.markdown("---")
    
    # Statistiques rapides
    st.markdown("### 📈 Stats Rapides")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Analyses", st.session_state.total_analyses)
    with col2:
        if st.session_state.total_analyses > 0:
            avg_conf = (st.session_state.stats['total_confidence'] / st.session_state.total_analyses) * 100
            st.metric("Confiance", f"{avg_conf:.1f}%")
        else:
            st.metric("Confiance", "N/A")

# ============================================================================
# PAGE PRINCIPALE
# ============================================================================
if page == "🏠 Accueil":
    # Header avec animation
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>🗑️ Smart Bin Detector</h1>
            <p style='color: white; font-size: 1.2rem; margin-top: 1rem;'>
                Classification intelligente avec YOLOv9
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Badges de statut
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div style='text-align: center; background: rgba(16, 185, 129, 0.2); padding: 1rem; border-radius: 12px; border: 2px solid #10b981;'>
                <h3 style='color: #10b981; margin: 0;'>✓ IA Active</h3>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style='text-align: center; background: rgba(59, 130, 246, 0.2); padding: 1rem; border-radius: 12px; border: 2px solid #3b82f6;'>
                <h3 style='color: #3b82f6; margin: 0;'>⚡ Temps Réel</h3>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div style='text-align: center; background: rgba(139, 92, 246, 0.2); padding: 1rem; border-radius: 12px; border: 2px solid #8b5cf6;'>
                <h3 style='color: #8b5cf6; margin: 0;'>🎯 Précis</h3>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Onglets principaux
    tab1, tab2 = st.tabs(["📤 Analyse d'Image", "🎥 Analyse Vidéo"])
    
    with tab1:
        st.markdown("### 📸 Uploader une image")
        
        # Upload d'image
        uploaded_file = st.file_uploader(
            "Choisissez une image de poubelle",
            type=['jpg', 'jpeg', 'png'],
            help="Formats acceptés: JPG, JPEG, PNG"
        )
        
        if uploaded_file:
            # Colonnes pour affichage
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🖼️ Image Originale")
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
                
                # Infos image
                with st.expander("ℹ️ Informations Image"):
                    st.write(f"**Dimensions:** {image.size[0]} x {image.size[1]} px")
                    st.write(f"**Format:** {image.format}")
                    st.write(f"**Mode:** {image.mode}")
            
            with col2:
                # Paramètres de détection
                with st.expander("⚙️ Paramètres", expanded=True):
                    confidence = st.slider(
                        "Seuil de confiance",
                        min_value=0.1,
                        max_value=0.9,
                        value=0.25,
                        step=0.05,
                        help="Seuil minimum de confiance pour la détection"
                    )
                
                # Bouton d'analyse
                if st.button("🔍 Analyser l'image", type="primary", use_container_width=True):
                    with st.spinner("🤖 Analyse en cours..."):
                        # Barre de progression animée
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        # Détection
                        result = detect_bin(image, model, confidence)
                        
                        # Mise à jour stats
                        st.session_state.total_analyses += 1
                        st.session_state.stats['total_confidence'] += result['confidence']
                        st.session_state.stats['total_time'] += result['processing_time']
                        
                        if result['status'] == 'PLEINE':
                            st.session_state.stats['pleine'] += 1
                        elif result['status'] == 'VIDE':
                            st.session_state.stats['vide'] += 1
                        
                        # Ajout à l'historique
                        st.session_state.analyses_history.insert(0, result)
                        if len(st.session_state.analyses_history) > 10:
                            st.session_state.analyses_history.pop()
                        
                        progress_bar.empty()
                    
                    # Affichage résultats
                    st.markdown("#### 🎯 Résultat de Détection")
                    
                    # Badge de statut
                    if result['status'] != 'AUCUNE_DETECTION':
                        status_class = "status-pleine" if result['status'] == "PLEINE" else "status-vide"
                        st.markdown(f"""
                            <div class='status-badge {status_class}'>
                                {result['emoji']} {result['status']}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Image avec détection
                        st.image(result['image_with_detection'], use_container_width=True)
                        
                        # Métriques
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        with metric_col1:
                            st.metric("Confiance", f"{result['confidence']*100:.1f}%")
                        with metric_col2:
                            st.metric("Temps", f"{result['processing_time']:.3f}s")
                        with metric_col3:
                            st.metric("Détections", result['num_detections'])
                        
                        # Barre de confiance
                        st.markdown("**Niveau de confiance:**")
                        st.progress(result['confidence'])
                        
                        # Message
                        if result['status'] == "PLEINE":
                            st.error(result['message'])
                        else:
                            st.success(result['message'])
                        
                        # Détails techniques
                        with st.expander("🔧 Détails Techniques"):
                            st.json({
                                'Classe': result['class_name'],
                                'Confiance': f"{result['confidence']:.4f}",
                                'Bounding Box': result['bbox'],
                                'Temps de traitement': f"{result['processing_time']:.3f}s"
                            })
                    else:
                        st.warning(result['message'])
                        st.image(image, use_container_width=True)
    
    with tab2:
        st.info("🚧 Fonctionnalité en développement - Analyse vidéo temps réel à venir!")
        st.markdown("""
        ### 🎥 Analyse Vidéo (Prochainement)
        
        Fonctionnalités prévues:
        - ✅ Analyse temps réel via webcam
        - ✅ Upload de fichiers vidéo
        - ✅ Détection multi-objets
        - ✅ Tracking des poubelles
        - ✅ Statistiques par frame
        """)

# ============================================================================
# PAGE STATISTIQUES
# ============================================================================
elif page == "📊 Statistiques":
    st.markdown("# 📊 Statistiques & Analyses")
    
    if st.session_state.total_analyses == 0:
        st.info("Aucune analyse effectuée pour le moment. Commencez par analyser une image!")
    else:
        # Métriques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Analyses",
                st.session_state.total_analyses,
                delta=f"+1" if st.session_state.total_analyses > 0 else None
            )
        
        with col2:
            avg_conf = (st.session_state.stats['total_confidence'] / st.session_state.total_analyses) * 100
            st.metric("Confiance Moyenne", f"{avg_conf:.1f}%")
        
        with col3:
            avg_time = st.session_state.stats['total_time'] / st.session_state.total_analyses
            st.metric("Temps Moyen", f"{avg_time:.3f}s")
        
        with col4:
            pleine_percent = (st.session_state.stats['pleine'] / st.session_state.total_analyses) * 100
            st.metric("Poubelles Pleines", f"{pleine_percent:.0f}%")
        
        st.markdown("---")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Camembert
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Pleines', 'Vides'],
                values=[st.session_state.stats['pleine'], st.session_state.stats['vide']],
                hole=0.4,
                marker_colors=['#ef4444', '#10b981']
            )])
            fig_pie.update_layout(
                title="Répartition des Détections",
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Historique confiance
            if st.session_state.analyses_history:
                confidences = [a['confidence']*100 for a in st.session_state.analyses_history[::-1]]
                fig_line = go.Figure(data=[go.Scatter(
                    y=confidences,
                    mode='lines+markers',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=10)
                )])
                fig_line.update_layout(
                    title="Évolution de la Confiance",
                    xaxis_title="Analyse #",
                    yaxis_title="Confiance (%)",
                    height=400
                )
                st.plotly_chart(fig_line, use_container_width=True)
        
        # Historique détaillé
        st.markdown("### 📜 Historique des Analyses")
        
        for idx, analysis in enumerate(st.session_state.analyses_history[:5]):
            with st.expander(f"#{idx+1} - {analysis['timestamp'].strftime('%H:%M:%S')} - {analysis['emoji']} {analysis['status']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Confiance:** {analysis['confidence']*100:.1f}%")
                with col2:
                    st.write(f"**Temps:** {analysis['processing_time']:.3f}s")
                with col3:
                    st.write(f"**Détections:** {analysis.get('num_detections', 'N/A')}")

# ============================================================================
# PAGE PARAMÈTRES
# ============================================================================
elif page == "⚙️ Paramètres":
    st.markdown("# ⚙️ Paramètres")
    
    st.markdown("### 🎨 Apparence")
    theme = st.selectbox("Thème", ["Clair", "Sombre", "Auto"])
    
    st.markdown("### 🔔 Notifications")
    enable_sound = st.checkbox("Activer les sons", value=False)
    enable_alerts = st.checkbox("Alertes poubelles pleines", value=True)
    
    st.markdown("### 🤖 Modèle")
    st.info(f"**Modèle actuel:** {Path(model_path).name}")
    st.write(f"**Classes:** {list(model.names.values())}")
    st.write(f"**Nombre de classes:** {len(model.names)}")
    
    st.markdown("### 💾 Données")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.analyses_history = []
            st.success("Historique effacé!")
    
    with col2:
        if st.button("📥 Exporter les stats", use_container_width=True):
            stats_json = json.dumps(st.session_state.stats, indent=2)
            st.download_button(
                "Télécharger stats.json",
                stats_json,
                file_name="stats.json",
                mime="application/json"
            )

# ============================================================================
# PAGE À PROPOS
# ============================================================================
elif page == "ℹ️ À propos":
    st.markdown("# ℹ️ À propos")
    
    st.markdown("""
    ## 🗑️ Smart Bin Detector
    
    ### 🎯 Mission
    Optimiser la gestion des déchets grâce à l'intelligence artificielle pour des villes plus propres et durables.
    
    ### 🚀 Technologies
    - **YOLOv9**: Détection d'objets en temps réel
    - **Streamlit**: Interface web interactive
    - **PyTorch**: Framework deep learning
    - **OpenCV**: Traitement d'images
    - **Plotly**: Visualisations interactives
    
    ### 📊 Performance
    - ✅ Précision > 90%
    - ✅ Temps de réponse < 1s
    - ✅ Support multi-formats
    - ✅ Interface responsive
    
    ### 👨‍💻 Développement
    **Auteur:** Dr Nourou  
    **Année:** 2025  
    **Version:** 1.0.0
    
    ### 📚 Ressources
    - [GitHub Repository](https://github.com/amadousarr04/detection_poubelle)
    - [Documentation YOLOv9](https://docs.ultralytics.com/)
    - [Streamlit Docs](https://docs.streamlit.io/)
    
    ---
    
    <div style='text-align: center; color: #667eea; font-size: 0.9rem;'>
        Développé avec ❤️ | Powered by YOLOv9 + Streamlit
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 1rem;'>
    🗑️ Smart Bin Detector v1.0.0 • 2025
</div>
""", unsafe_allow_html=True)
