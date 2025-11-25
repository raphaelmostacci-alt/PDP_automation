"""
Module d'analyse et d'extraction de données des documents
Supporte PDFs (texte et images) et images (JPG, PNG, etc.)
"""

import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

# Imports conditionnels (seront installés via requirements.txt)
try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

from config import OCR_LANGUAGE, OCR_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """Analyseur de documents avec OCR et parsing PDF"""
    
    def __init__(self):
        """Initialise l'analyseur"""
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie que les dépendances nécessaires sont installées"""
        if not PyPDF2 or not pdfplumber:
            logger.warning("⚠️ PyPDF2 ou pdfplumber non installé. Fonctionnalités PDF limitées.")
        
        if not Image or not pytesseract:
            logger.warning("⚠️ Pillow ou pytesseract non installé. OCR non disponible.")
    
    def analyze_document(self, file_path: str, doc_type: str = "UNKNOWN") -> Dict:
        """
        Analyse un document et extrait les informations pertinentes
        
        Args:
            file_path: Chemin du fichier à analyser
            doc_type: Type de document (CNI, HABILITATION_ELEC, FDS, etc.)
        
        Returns:
            Dictionnaire contenant les données extraites
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        logger.info(f"📄 Analyse de: {file_path.name}")
        
        # Extraire le texte selon le type de fichier
        if extension == '.pdf':
            text = self._extract_text_from_pdf(file_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            text = self._extract_text_from_image(file_path)
        else:
            logger.error(f"Format non supporté: {extension}")
            return {'error': 'Format non supporté'}
        
        # Analyser le texte extrait selon le type de document
        if doc_type == "CNI":
            return self._analyze_cni(text)
        elif doc_type == "HABILITATION_ELEC":
            return self._analyze_habilitation_elec(text)
        elif doc_type == "FDS":
            return self._analyze_fds(text)
        elif doc_type == "APTITUDE_FRIGO":
            return self._analyze_aptitude_frigo(text)
        else:
            return {
                'raw_text': text[:500],  # Premiers 500 caractères
                'full_text': text
            }
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """
        Extrait le texte d'un PDF (texte natif ou OCR si nécessaire)
        
        Args:
            file_path: Chemin du fichier PDF
        
        Returns:
            Texte extrait
        """
        text = ""
        
        # Essayer d'abord pdfplumber (meilleur pour le texte natif)
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Erreur pdfplumber: {e}")
        
        # Si pas de texte, essayer PyPDF2
        if not text and PyPDF2:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Erreur PyPDF2: {e}")
        
        # Si toujours pas de texte, c'est probablement un PDF scanné -> OCR
        if not text or len(text.strip()) < 50:
            logger.info("📸 PDF scanné détecté, utilisation de l'OCR...")
            text = self._ocr_pdf_pages(file_path)
        
        return text
    
    def _ocr_pdf_pages(self, file_path: Path) -> str:
        """
        Applique l'OCR sur les pages d'un PDF
        
        Args:
            file_path: Chemin du fichier PDF
        
        Returns:
            Texte extrait par OCR
        """
        if not Image or not pytesseract:
            logger.error("❌ OCR non disponible (Pillow ou pytesseract manquant)")
            return ""
        
        # Convertir PDF en images et appliquer OCR
        # Note: Nécessite pdf2image (sera dans requirements.txt)
        try:
            from pdf2image import convert_from_path
            
            images = convert_from_path(file_path)
            text = ""
            
            for i, image in enumerate(images):
                logger.info(f"OCR page {i+1}/{len(images)}")
                page_text = pytesseract.image_to_string(image, lang=OCR_LANGUAGE, config=OCR_CONFIG)
                text += page_text + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Erreur OCR PDF: {e}")
            return ""
    
    def _extract_text_from_image(self, file_path: Path) -> str:
        """
        Extrait le texte d'une image via OCR
        
        Args:
            file_path: Chemin du fichier image
        
        Returns:
            Texte extrait
        """
        if not Image or not pytesseract:
            logger.error("❌ OCR non disponible")
            return ""
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang=OCR_LANGUAGE, config=OCR_CONFIG)
            return text
        except Exception as e:
            logger.error(f"Erreur OCR image: {e}")
            return ""
    
    def _analyze_cni(self, text: str) -> Dict:
        """
        Analyse une Carte Nationale d'Identité
        
        Args:
            text: Texte extrait du document
        
        Returns:
            Données extraites (nom, prénom, date de validité)
        """
        data = {
            'nom': self._extract_nom(text),
            'prenom': self._extract_prenom(text),
            'date_expiration': self._extract_date_expiration(text),
            'raw_text': text
        }
        return data
    
    def _analyze_habilitation_elec(self, text: str) -> Dict:
        """
        Analyse une habilitation électrique
        
        Args:
            text: Texte extrait du document
        
        Returns:
            Données extraites
        """
        data = {
            'nom': self._extract_nom(text),
            'prenom': self._extract_prenom(text),
            'date_delivrance': self._extract_date_delivrance(text),
            'niveau_habilitation': self._extract_niveau_habilitation(text),
            'raw_text': text
        }
        return data
    
    def _analyze_fds(self, text: str) -> Dict:
        """
        Analyse une Fiche de Données de Sécurité
        
        Args:
            text: Texte extrait du document
        
        Returns:
            Données extraites
        """
        data = {
            'produit': self._extract_nom_produit(text),
            'annee_publication': self._extract_annee_publication(text),
            'date_revision': self._extract_date_revision(text),
            'raw_text': text
        }
        return data
    
    def _analyze_aptitude_frigo(self, text: str) -> Dict:
        """
        Analyse une aptitude frigorifique
        
        Args:
            text: Texte extrait du document
        
        Returns:
            Données extraites
        """
        data = {
            'nom': self._extract_nom(text),
            'prenom': self._extract_prenom(text),
            'categorie': self._extract_categorie_frigo(text),
            'raw_text': text
        }
        return data
    
    # ==========================================
    # FONCTIONS D'EXTRACTION PAR REGEX
    # ==========================================
    
    def _extract_nom(self, text: str) -> Optional[str]:
        """Extrait le nom de famille"""
        patterns = [
            r'Nom[:\s]+([A-ZÀÉÈÊËÏÔÙÛÇ\-\s]+)',
            r'Surname[:\s]+([A-ZÀÉÈÊËÏÔÙÛÇ\-\s]+)',
            r'NOM[:\s]+([A-ZÀÉÈÊËÏÔÙÛÇ\-\s]+)'
        ]
        return self._extract_with_patterns(text, patterns)
    
    def _extract_prenom(self, text: str) -> Optional[str]:
        """Extrait le prénom"""
        patterns = [
            r'Prénom[:\s]+([A-ZÀÉÈÊËÏÔÙÛÇa-zàéèêëïôùûç\-\s]+)',
            r'Prenom[:\s]+([A-ZÀÉÈÊËÏÔÙÛÇa-zàéèêëïôùûç\-\s]+)',
            r'Given names?[:\s]+([A-ZÀÉÈÊËÏÔÙÛÇa-zàéèêëïôùûç\-\s]+)'
        ]
        return self._extract_with_patterns(text, patterns)
    
    def _extract_date_expiration(self, text: str) -> Optional[datetime]:
        """Extrait la date d'expiration"""
        patterns = [
            r'Valable jusqu\'au[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})',
            r'Valid until[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})',
            r'Expire le[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})',
            r'(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})'
        ]
        date_str = self._extract_with_patterns(text, patterns)
        return self._parse_date(date_str) if date_str else None
    
    def _extract_date_delivrance(self, text: str) -> Optional[datetime]:
        """Extrait la date de délivrance"""
        patterns = [
            r'Délivré le[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})',
            r'Date de délivrance[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})',
            r'Issued on[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})'
        ]
        date_str = self._extract_with_patterns(text, patterns)
        return self._parse_date(date_str) if date_str else None
    
    def _extract_annee_publication(self, text: str) -> Optional[int]:
        """Extrait l'année de publication"""
        patterns = [
            r'Version[:\s]+\d+[\/\.\-](\d{4})',
            r'Date de révision[:\s]+\d{2}[\/\.\-]\d{2}[\/\.\-](\d{4})',
            r'(\d{4})'
        ]
        year_str = self._extract_with_patterns(text, patterns)
        try:
            return int(year_str) if year_str else None
        except ValueError:
            return None
    
    def _extract_date_revision(self, text: str) -> Optional[datetime]:
        """Extrait la date de révision"""
        patterns = [
            r'Date de révision[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})',
            r'Revision date[:\s]+(\d{2}[\/\.\-]\d{2}[\/\.\-]\d{4})'
        ]
        date_str = self._extract_with_patterns(text, patterns)
        return self._parse_date(date_str) if date_str else None
    
    def _extract_nom_produit(self, text: str) -> Optional[str]:
        """Extrait le nom du produit (FDS)"""
        patterns = [
            r'Produit[:\s]+([^\n]+)',
            r'Nom du produit[:\s]+([^\n]+)',
            r'Product name[:\s]+([^\n]+)'
        ]
        return self._extract_with_patterns(text, patterns)
    
    def _extract_niveau_habilitation(self, text: str) -> Optional[str]:
        """Extrait le niveau d'habilitation électrique"""
        patterns = [
            r'Niveau[:\s]+([BH][0-9VRT]+)',
            r'Habilitation[:\s]+([BH][0-9VRT]+)',
            r'([BH][0-9VRT]+)'
        ]
        return self._extract_with_patterns(text, patterns)
    
    def _extract_categorie_frigo(self, text: str) -> Optional[str]:
        """Extrait la catégorie frigorifique"""
        patterns = [
            r'Catégorie[:\s]+([IVX]+)',
            r'Cat\.[:\s]+([IVX]+)'
        ]
        return self._extract_with_patterns(text, patterns)
    
    def _extract_with_patterns(self, text: str, patterns: list) -> Optional[str]:
        """
        Essaie plusieurs patterns regex pour extraire une information
        
        Args:
            text: Texte à analyser
            patterns: Liste de patterns regex
        
        Returns:
            Première correspondance trouvée ou None
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse une date depuis différents formats
        
        Args:
            date_str: Chaîne représentant une date
        
        Returns:
            Objet datetime ou None
        """
        if not date_str:
            return None
        
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%d.%m.%Y',
            '%Y/%m/%d',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Format de date non reconnu: {date_str}")
        return None


def main():
    """Fonction de test de l'analyseur"""
    analyzer = DocumentAnalyzer()
    
    # Test avec le fichier CNI fourni
    test_file = Path("/home/raphaelmostacci/PDP_automation/CNI Stephane FOUQUES.PDF")
    
    if test_file.exists():
        print(f"\n🔍 Test d'analyse de: {test_file.name}")
        result = analyzer.analyze_document(str(test_file), "CNI")
        
        print("\n📊 Résultats:")
        for key, value in result.items():
            if key != 'raw_text' and key != 'full_text':
                print(f"  {key}: {value}")
    else:
        print(f"❌ Fichier de test non trouvé: {test_file}")


if __name__ == "__main__":
    main()
