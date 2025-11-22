# 🗑️ Détecteur de Poubelles - Application Fullstack

Application web complète de classification intelligente de poubelles (PLEINE/VIDE) avec YOLOv9.

## 📋 Architecture

```
Frontend (HTML/CSS/JS) ← HTTP → Backend (FastAPI) ← YOLOv9 Model
```

- **Frontend**: Interface web moderne avec drag-and-drop
- **Backend**: API REST FastAPI pour inférence YOLOv9
- **Modèle**: YOLOv9 entraîné sur dataset personnalisé (2 classes)

## 🚀 Déploiement sur Render (sans Docker)

### Prérequis

1. Compte GitHub
2. Compte Render.com
3. Fichier `best.pt` (modèle entraîné)

### Étape 1: Préparer le projet

```bash
# Copier le modèle dans le backend
copy best.pt fullstack-poubelle-app\backend\best.pt

# Initialiser Git
cd fullstack-poubelle-app
git init
git add .
git commit -m "Initial commit - Detecteur de Poubelles"

# Pusher sur GitHub
git remote add origin https://github.com/VOTRE-USERNAME/detecteur-poubelles.git
git push -u origin main
```

### Étape 2: Déployer sur Render

#### Option A: Avec render.yaml (Blueprint)

1. Aller sur https://dashboard.render.com/
2. Cliquer sur "New" → "Blueprint"
3. Connecter votre repository GitHub
4. Render détectera automatiquement `render.yaml`
5. Cliquer sur "Apply" pour déployer

#### Option B: Manuellement

**Backend:**

1. Créer un nouveau "Web Service"
2. Configuration:
   - **Name**: detecteur-poubelles-backend
   - **Environment**: Python
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11

**Frontend:**

1. Créer un nouveau "Static Site"
2. Configuration:
   - **Name**: detecteur-poubelles-frontend
   - **Build Command**: `echo "No build needed"`
   - **Publish Directory**: `frontend`

3. Dans `frontend/script.js`, mettre à jour l'URL de l'API:
   ```javascript
   const API_URL = 'https://detecteur-poubelles-backend.onrender.com';
   ```

### Étape 3: Tester

Une fois déployé, vous recevrez 2 URLs:
- Frontend: `https://detecteur-poubelles-frontend.onrender.com`
- Backend: `https://detecteur-poubelles-backend.onrender.com`

Testez l'API: `https://detecteur-poubelles-backend.onrender.com/docs`

## 💻 Développement Local

### Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer dépendances
pip install -r requirements.txt

# Copier le modèle
copy ..\best.pt .  # Windows
# cp ../best.pt .  # Linux/Mac

# Démarrer le serveur
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend accessible sur: http://127.0.0.1:8000

Documentation API: http://127.0.0.1:8000/docs

### Frontend

```bash
# Ouvrir simplement index.html dans le navigateur
# OU utiliser un serveur HTTP simple:

# Python
cd frontend
python -m http.server 3000

# Node.js
npx serve frontend -p 3000
```

Frontend accessible sur: http://localhost:3000

## 📁 Structure du Projet

```
fullstack-poubelle-app/
├── backend/
│   ├── main.py                # API FastAPI
│   ├── requirements.txt       # Dépendances Python
│   └── best.pt               # Modèle YOLOv9 (à ajouter)
│
├── frontend/
│   ├── index.html            # Page principale
│   ├── styles.css            # Styles CSS
│   └── script.js             # Logique JavaScript
│
├── render.yaml               # Configuration Render
└── README.md                 # Documentation
```

## 🛠️ Technologies

### Backend
- **FastAPI** 0.104.1 - Framework web Python
- **Ultralytics** 8.3+ - YOLOv9
- **PyTorch** 2.5+ - Deep learning
- **Uvicorn** - Serveur ASGI
- **Python** 3.11

### Frontend
- **HTML5** - Structure
- **CSS3** - Design moderne avec animations
- **JavaScript ES6** - Logique interactive
- **Fetch API** - Communication avec backend

## 🔧 Configuration

### Variables d'environnement (Backend)

```bash
PORT=8000              # Port du serveur (auto sur Render)
```

### Configuration Frontend

Modifier `script.js` ligne 7-9:
```javascript
const API_URL = window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000'  // Dev local
    : 'https://VOTRE-BACKEND.onrender.com';  // Production
```

## 📊 Endpoints API

### `GET /`
Page d'accueil de l'API

### `GET /health`
Vérification de l'état du serveur
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "..."
}
```

### `POST /predict`
Classification d'une image

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image JPG/PNG/JPEG)

**Response:**
```json
{
  "success": true,
  "status": "PLEINE",
  "emoji": "🔴",
  "color": "#ef4444",
  "message": "⚠️ Collecte requise immédiatement!",
  "confidence": 0.9234,
  "confidence_percent": 92.34,
  "class_name": "poubelle_pleine",
  "processing_time": 0.342
}
```

### `GET /model-info`
Informations sur le modèle

## 🎨 Fonctionnalités

✅ Upload d'images par drag-and-drop  
✅ Prévisualisation avant analyse  
✅ Classification en temps réel  
✅ Affichage du niveau de confiance  
✅ Design moderne et responsive  
✅ Animations fluides  
✅ Gestion d'erreurs complète  
✅ Compatible mobile  

## 🐛 Dépannage

### Erreur "Failed to fetch"
- Vérifier que le backend est démarré
- Vérifier l'URL de l'API dans `script.js`
- Vérifier les CORS dans `main.py`

### Erreur "best.pt not found"
- Copier le fichier `best.pt` dans `backend/`
- Vérifier les chemins dans `MODEL_PATHS`

### Erreur NumPy sur Render
- Utiliser Python 3.11 (pas 3.13)
- Les dépendances dans `requirements.txt` sont compatibles

## 📱 Responsive

L'application est entièrement responsive et fonctionne sur:
- 💻 Desktop
- 📱 Mobile
- 📲 Tablette

## 🔒 Sécurité

- Validation des types de fichiers
- Limite de taille (10 MB)
- CORS configuré
- Gestion d'erreurs robuste

## 📈 Performance

- Temps de traitement: ~0.3-0.7s par image
- Support CPU uniquement (pas de GPU requis sur Render)
- Chargement lazy du modèle

## 🎯 Classes détectées

1. **poubelle_pleine** 🔴 - Priorité HAUTE
2. **poubelle_vide** 🟢 - Priorité BASSE

## 📄 Licence

Projet académique - 2025

## 👨‍💻 Auteur

Développé dans le cadre du cours IA - Dr Nourou

---

**Développé avec ❤️ | Powered by YOLOv9 + FastAPI**
