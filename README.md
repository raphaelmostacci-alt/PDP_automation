# 🚀 AUTOMATISATION PDP - Vérification de Conformité

Système automatisé de vérification de conformité des documents pour les Plans de Prévention (PDP).

## 📋 Description

Ce système analyse automatiquement les documents obligatoires pour les entreprises extérieures intervenant dans votre laboratoire :
- **Cartes Nationales d'Identité (CNI)**
- **Habilitations Électriques**
- **Fiches de Données de Sécurité (FDS)**
- **Aptitudes Frigorifiques**

Il génère un **rapport Excel** complet avec le statut de conformité de chaque document.

## ✨ Fonctionnalités

- ✅ **Scan automatique** des documents (PDF, images)
- ✅ **Extraction OCR** pour documents scannés
- ✅ **Intégration ChatGPT** optionnelle pour améliorer l'extraction
- ✅ **Validation automatique** selon les règles métier
- ✅ **Rapport Excel** avec mise en forme et statistiques

## 📦 Prérequis

### 1. Python 3.8+
Vérifiez votre version :
```bash
python --version
```

### 2. Tesseract OCR
**Important** : Tesseract doit être installé séparément.

#### Sur Windows :
1. Téléchargez l'installateur : https://github.com/UB-Mannheim/tesseract/wiki
2. Installez-le (notez le chemin d'installation)
3. Ajoutez au PATH ou configurez dans le code

#### Sur Linux :
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-fra
```

#### Sur macOS :
```bash
brew install tesseract tesseract-lang
```

### 3. Poppler (pour pdf2image)
#### Sur Windows :
1. Téléchargez Poppler : https://github.com/oschwartz10612/poppler-windows/releases/
2. Extrayez et ajoutez `bin/` au PATH

#### Sur Linux :
```bash
sudo apt-get install poppler-utils
```

#### Sur macOS :
```bash
brew install poppler
```

## 🛠️ Installation

### 1. Cloner ou télécharger le projet
```bash
cd /chemin/vers/PDP_automation
```

### 2. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv

# Activer l'environnement
# Sur Windows :
venv\Scripts\activate

# Sur Linux/Mac :
source venv/bin/activate
```

### 3. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 4. Installer ChromeDriver (pour Selenium)
Le package `webdriver-manager` l'installera automatiquement au premier lancement.

## 📁 Structure du Projet

```
PDP_automation/
├── main.py                  # Point d'entrée principal
├── config.py                # Configuration et règles de validité
├── document_scanner.py      # Scanner de fichiers
├── document_analyzer.py     # Extraction de données (OCR)
├── chatgpt_client.py        # Client ChatGPT (Selenium)
├── validator.py             # Validation de conformité
├── excel_generator.py       # Génération de rapports Excel
├── requirements.txt         # Dépendances Python
├── .env.example            # Template de configuration
├── README.md               # Cette documentation
└── data/
    ├── input/              # 📥 Placez vos documents ICI
    └── output/             # 📤 Rapports Excel générés
```

## 🚀 Utilisation

### 1. Organiser vos documents
Placez vos documents dans `data/input/` avec cette structure :

```
data/input/
├── Entreprise_A/
│   ├── CNI_DUPONT.pdf
│   ├── HAB_DUPONT.pdf
│   └── FDS_Produit.pdf
├── Entreprise_B/
│   ├── CNI_MARTIN.jpg
│   └── APTITUDE_MARTIN.pdf
└── ...
```

### 2. Lancer l'analyse

#### Mode de base (OCR seul) :
```bash
python main.py
```

#### Avec ChatGPT (meilleure précision) :
```bash
python main.py --use-chatgpt
```

**Note** : Le navigateur s'ouvrira, connectez-vous manuellement à https://chat.st.com/ puis revenez au terminal.

#### Mode production (sans interface) :
```bash
python main.py --use-chatgpt --headless
```

### 3. Récupérer le rapport
Le rapport Excel sera généré dans `data/output/` avec le format :
```
Rapport_PDP_AAAAMMJJ_HHMMSS.xlsx
```

## 📊 Format du Rapport Excel

Le rapport contient :
- **Entreprise** : Nom de l'entreprise
- **Nom / Prénom** : Identité de la personne
- **Type Document** : CNI, HABILITATION_ELEC, FDS, APTITUDE_FRIGO
- **Fichier** : Nom du fichier source
- **Date Validité** : Date d'expiration ou année
- **Statut** : ✅ CONFORME / ❌ NON CONFORME / ⚠️ ERREUR / 🔍 À VÉRIFIER
- **Commentaire** : Détails sur la validation

## ⚙️ Configuration

### Règles de Validité (config.py)

```python
# CNI
CNI_VALIDITY_YEARS = 10

# Habilitations Électriques
HABILITATION_ELEC_VALIDITY_YEARS = 3

# FDS
FDS_MIN_YEAR = 2021

# Aptitudes Frigorifiques
APTITUDE_FRIGO_LIFETIME = True  # Valides à vie
```

Modifiez ces valeurs selon vos besoins.

### URL ChatGPT

Dans `config.py` :
```python
CHATGPT_URL = "https://chat.st.com/"  # Votre URL ChatGPT
```

## 🧪 Tests

Chaque module peut être testé individuellement :

```bash
# Test du scanner
python document_scanner.py

# Test de l'analyseur
python document_analyzer.py

# Test du validateur
python validator.py

# Test du générateur Excel
python excel_generator.py

# Test du client ChatGPT
python chatgpt_client.py
```

## 🐛 Dépannage

### Erreur "tesseract not found"
- **Windows** : Ajoutez Tesseract au PATH ou spécifiez le chemin :
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  ```
- **Linux/Mac** : Réinstallez avec `sudo apt install tesseract-ocr`

### Erreur "Unable to get page count"
- Installez Poppler (voir prérequis)

### ChatGPT ne se connecte pas
- Vérifiez que vous êtes sur le réseau ST
- Vérifiez l'URL dans `config.py`
- Essayez sans `--headless` pour voir l'interface

### Erreur "ChromeDriver"
- Vérifiez votre connexion internet (téléchargement auto)
- Ou téléchargez manuellement : https://chromedriver.chromium.org/

## 📝 Améliorations Futures

- [ ] Support d'autres types de documents
- [ ] API REST pour intégration
- [ ] Interface web (Flask/Django)
- [ ] Notifications email automatiques
- [ ] Base de données pour historique
- [ ] Support multilingue

## 🔒 Sécurité

- ⚠️ Ne commitez JAMAIS le dossier `data/input/` (documents sensibles)
- ⚠️ Ne commitez JAMAIS les fichiers `.env` (credentials)
- ✅ Utilisez `.gitignore` pour protéger ces fichiers

## 📞 Support

Pour toute question ou problème :
1. Vérifiez les logs dans `data/output/pdp_automation.log`
2. Consultez cette documentation
3. Testez chaque module individuellement

## 📜 Licence

Usage interne ST uniquement.

---

**Version** : 1.0  
**Date** : Novembre 2025  
**Auteur** : Automatisation PDP System
