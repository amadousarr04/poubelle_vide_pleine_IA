# 🗑️ Smart Bin Detector - Application Streamlit

Application web professionnelle pour la classification intelligente de poubelles avec YOLOv9.

## ✨ Fonctionnalités

### 🏠 Accueil
- **Upload d'images** : Glisser-déposer ou parcourir
- **Analyse en temps réel** : Détection instantanée PLEINE/VIDE
- **Visualisation** : Bounding boxes colorées sur l'image
- **Métriques** : Confiance, temps de traitement, nombre de détections
- **Paramètres ajustables** : Seuil de confiance personnalisable

### 📊 Statistiques
- **Métriques globales** : Total analyses, confiance moyenne, temps moyen
- **Graphiques interactifs** :
  - Camembert : Répartition PLEINE/VIDE
  - Courbe : Évolution de la confiance
- **Historique** : 10 dernières analyses détaillées

### ⚙️ Paramètres
- **Apparence** : Thème clair/sombre/auto
- **Notifications** : Sons et alertes
- **Modèle** : Informations détaillées
- **Données** : Export stats JSON, effacement historique

### ℹ️ À propos
- Mission du projet
- Technologies utilisées
- Performance et ressources

## 🚀 Installation

### 1. Prérequis
```bash
Python 3.11+
```

### 2. Installation des dépendances
```bash
cd streamlit_app
pip install -r requirements.txt
```

### 3. Placer le modèle
Copiez `best.pt` dans l'un de ces emplacements :
- `streamlit_app/best.pt`
- `streamlit_app/../best.pt`
- `streamlit_app/backend/best.pt`

### 4. Lancer l'application
```bash
streamlit run app.py
```

L'application démarre sur : **http://localhost:8501**

## 📱 Utilisation

1. **Accédez à l'application** dans votre navigateur
2. **Uploadez une image** de poubelle (JPG, PNG, JPEG)
3. **Ajustez le seuil de confiance** si nécessaire (défaut: 0.25)
4. **Cliquez sur "Analyser"** 🔍
5. **Consultez les résultats** :
   - Status : PLEINE 🔴 / VIDE 🟢
   - Confiance en %
   - Image avec bounding box
   - Message d'action
6. **Explorez les statistiques** 📊

## 🎨 Design

### Gradient Animé
Fond avec dégradé violet-bleu en mouvement perpétuel

### Glassmorphisme
Cartes semi-transparentes avec effet de flou

### Animations
- Fade in sur titre principal
- Slide up sur cartes
- Pulse sur badges de statut
- Hover effects sur boutons

### Couleurs
- **PLEINE** : Rouge (#ef4444)
- **VIDE** : Vert (#10b981)
- **Primaire** : Violet (#667eea, #764ba2)

## 📊 Structure

```
streamlit_app/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
├── README.md          # Documentation
└── best.pt            # Modèle YOLOv9 (à ajouter)
```

## 🔧 Technologies

- **Streamlit** : Framework web Python
- **YOLOv9** : Détection d'objets (Ultralytics)
- **PyTorch** : Deep learning
- **OpenCV** : Traitement d'images
- **Plotly** : Graphiques interactifs
- **NumPy** : Calculs numériques

## 📈 Métriques Trackées

- Nombre total d'analyses
- Confiance moyenne des détections
- Temps de traitement moyen
- Répartition PLEINE/VIDE
- Historique des 10 dernières analyses

## 🎯 Cas d'Usage

- **Municipalités** : Suivi de remplissage des bacs publics
- **Entreprises** : Optimisation de la collecte
- **Smart Cities** : Intégration IoT
- **Recherche** : Analyse de données déchets

## 🔮 Améliorations Futures

- [ ] Analyse vidéo temps réel
- [ ] Détection webcam
- [ ] Multi-tracking
- [ ] Export PDF des rapports
- [ ] API REST intégrée
- [ ] Notifications email
- [ ] Géolocalisation des poubelles

## 📄 Licence

Projet développé dans le cadre du cours IA de Dr Nourou - 2025

## 👨‍💻 Auteur

**Dr Nourou**  
Cours IA - 2025

---

**Version** : 1.0.0  
**Dernière mise à jour** : Novembre 2025
