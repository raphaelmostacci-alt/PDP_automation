"""
Configuration du système d'automatisation PDP
Règles de validité et paramètres généraux
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

# ==========================================
# CHEMINS DES DOSSIERS
# ==========================================
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# ==========================================
# CONFIGURATION CHATGPT
# ==========================================
CHATGPT_URL = "https://chat.st.com/"  # URL du ChatGPT de votre entreprise
CHATGPT_USE_SELENIUM = True  # True si pas d'API disponible

# ==========================================
# RÈGLES DE VALIDITÉ DES DOCUMENTS
# ==========================================

# Carte Nationale d'Identité (CNI)
CNI_VALIDITY_YEARS = 10  # Validité standard pour adultes
CNI_EXTENDED_VALIDITY_YEARS = 15  # Prolongation automatique possible

# Habilitations Électriques
HABILITATION_ELEC_VALIDITY_YEARS = 3

# Fiches de Données de Sécurité (FDS)
FDS_MIN_YEAR = 2021  # Les FDS doivent être >= 2021

# Aptitudes Frigorifiques
APTITUDE_FRIGO_LIFETIME = True  # Valides à vie

# ==========================================
# TYPES DE DOCUMENTS RECONNUS
# ==========================================
DOCUMENT_TYPES = {
    "CNI": ["cni", "carte", "identite", "identity"],
    "HABILITATION_ELEC": ["habilitation", "electrique", "electric"],
    "FDS": ["fds", "fiche", "securite", "safety"],
    "APTITUDE_FRIGO": ["aptitude", "frigo", "frigorifique", "refrigeration"]
}

# ==========================================
# EXTENSIONS DE FICHIERS SUPPORTÉES
# ==========================================
SUPPORTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff']

# ==========================================
# CONFIGURATION OCR
# ==========================================
OCR_LANGUAGE = 'fra'  # Français
OCR_CONFIG = '--oem 3 --psm 6'  # Mode OCR optimal

# ==========================================
# CONFIGURATION EXCEL
# ==========================================
EXCEL_FILENAME_TEMPLATE = "Rapport_PDP_{date}.xlsx"
EXCEL_SHEET_NAME = "Conformité Documents"

# Colonnes du rapport Excel
EXCEL_COLUMNS = [
    "Entreprise",
    "Nom Personne",
    "Prénom Personne",
    "Type Document",
    "Fichier",
    "Date Validité",
    "Statut",
    "Commentaire"
]

# ==========================================
# STATUTS DE CONFORMITÉ
# ==========================================
STATUS_CONFORME = "✅ CONFORME"
STATUS_NON_CONFORME = "❌ NON CONFORME"
STATUS_ERREUR = "⚠️ ERREUR"
STATUS_A_VERIFIER = "🔍 À VÉRIFIER"

# ==========================================
# CONFIGURATION LOGGING
# ==========================================
LOG_LEVEL = "INFO"
LOG_FILE = OUTPUT_DIR / "pdp_automation.log"

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def get_current_date():
    """Retourne la date actuelle"""
    return datetime.now()

def get_excel_filename():
    """Génère le nom du fichier Excel avec la date"""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return EXCEL_FILENAME_TEMPLATE.format(date=date_str)

def is_document_expired(expiry_date, buffer_days=0):
    """
    Vérifie si un document est expiré
    
    Args:
        expiry_date: Date d'expiration (datetime)
        buffer_days: Nombre de jours de marge (optionnel)
    
    Returns:
        bool: True si expiré, False sinon
    """
    if not expiry_date:
        return None
    
    current_date = get_current_date()
    if buffer_days > 0:
        current_date += timedelta(days=buffer_days)
    
    return expiry_date < current_date

def validate_cni(expiry_date):
    """
    Valide une CNI selon les règles françaises
    
    Args:
        expiry_date: Date d'expiration de la CNI
    
    Returns:
        tuple: (is_valid, message)
    """
    if not expiry_date:
        return False, "Date d'expiration non trouvée"
    
    is_expired = is_document_expired(expiry_date)
    
    if is_expired:
        return False, f"CNI expirée le {expiry_date.strftime('%d/%m/%Y')}"
    else:
        return True, f"CNI valide jusqu'au {expiry_date.strftime('%d/%m/%Y')}"

def validate_habilitation_elec(issue_date):
    """
    Valide une habilitation électrique (validité 3 ans)
    
    Args:
        issue_date: Date de délivrance
    
    Returns:
        tuple: (is_valid, message)
    """
    if not issue_date:
        return False, "Date de délivrance non trouvée"
    
    expiry_date = issue_date + timedelta(days=HABILITATION_ELEC_VALIDITY_YEARS * 365)
    is_expired = is_document_expired(expiry_date)
    
    if is_expired:
        return False, f"Habilitation expirée le {expiry_date.strftime('%d/%m/%Y')}"
    else:
        return True, f"Habilitation valide jusqu'au {expiry_date.strftime('%d/%m/%Y')}"

def validate_fds(release_year):
    """
    Valide une FDS (doit être >= 2021)
    
    Args:
        release_year: Année de publication
    
    Returns:
        tuple: (is_valid, message)
    """
    if not release_year:
        return False, "Année de publication non trouvée"
    
    if release_year >= FDS_MIN_YEAR:
        return True, f"FDS à jour (année {release_year})"
    else:
        return False, f"FDS obsolète (année {release_year}, minimum requis: {FDS_MIN_YEAR})"

def validate_aptitude_frigo():
    """
    Valide une aptitude frigorifique (valide à vie)
    
    Returns:
        tuple: (is_valid, message)
    """
    return True, "Aptitude frigorifique valide à vie"

# ==========================================
# VALIDATION DE LA CONFIGURATION
# ==========================================

def validate_config():
    """Vérifie que la configuration est valide"""
    errors = []
    
    # Vérifier que les dossiers existent
    if not INPUT_DIR.exists():
        errors.append(f"Le dossier d'entrée n'existe pas: {INPUT_DIR}")
    
    if not OUTPUT_DIR.exists():
        errors.append(f"Le dossier de sortie n'existe pas: {OUTPUT_DIR}")
    
    return errors

if __name__ == "__main__":
    # Test de la configuration
    print("=== Configuration PDP Automation ===")
    print(f"Dossier d'entrée: {INPUT_DIR}")
    print(f"Dossier de sortie: {OUTPUT_DIR}")
    print(f"URL ChatGPT: {CHATGPT_URL}")
    print(f"\nRègles de validité:")
    print(f"- CNI: {CNI_VALIDITY_YEARS} ans")
    print(f"- Habilitation électrique: {HABILITATION_ELEC_VALIDITY_YEARS} ans")
    print(f"- FDS: >= {FDS_MIN_YEAR}")
    print(f"- Aptitude frigo: Valide à vie")
    
    errors = validate_config()
    if errors:
        print("\n⚠️ Erreurs de configuration:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configuration valide")
