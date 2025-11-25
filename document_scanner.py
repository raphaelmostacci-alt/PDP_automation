"""
Module de scan et d'inventaire des fichiers à analyser
"""

import os
from pathlib import Path
from typing import List, Dict
import logging
from config import INPUT_DIR, SUPPORTED_EXTENSIONS, DOCUMENT_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentScanner:
    """Scanner de documents pour le système PDP"""
    
    def __init__(self, input_directory: Path = INPUT_DIR):
        """
        Initialise le scanner
        
        Args:
            input_directory: Chemin du dossier contenant les documents
        """
        self.input_dir = Path(input_directory)
        self.documents = []
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Le dossier d'entrée n'existe pas: {self.input_dir}")
    
    def scan_documents(self) -> List[Dict]:
        """
        Scanne tous les documents dans le dossier d'entrée
        
        Returns:
            Liste de dictionnaires contenant les informations des documents
        """
        logger.info(f"📁 Scan du dossier: {self.input_dir}")
        self.documents = []
        
        # Parcourir récursivement tous les fichiers
        for file_path in self.input_dir.rglob('*'):
            if file_path.is_file() and self._is_supported_file(file_path):
                doc_info = self._extract_file_info(file_path)
                self.documents.append(doc_info)
        
        logger.info(f"✅ {len(self.documents)} document(s) trouvé(s)")
        return self.documents
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """
        Vérifie si le fichier est supporté
        
        Args:
            file_path: Chemin du fichier
        
        Returns:
            True si l'extension est supportée, False sinon
        """
        return file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    
    def _extract_file_info(self, file_path: Path) -> Dict:
        """
        Extrait les informations de base d'un fichier
        
        Args:
            file_path: Chemin du fichier
        
        Returns:
            Dictionnaire contenant les informations du fichier
        """
        # Extraire le chemin relatif par rapport au dossier d'entrée
        relative_path = file_path.relative_to(self.input_dir)
        
        # Essayer de déduire l'entreprise du nom du dossier parent
        parts = relative_path.parts
        entreprise = parts[0] if len(parts) > 1 else "Non spécifié"
        
        # Essayer de déduire le type de document du nom de fichier
        doc_type = self._guess_document_type(file_path.name)
        
        return {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'relative_path': str(relative_path),
            'entreprise': entreprise,
            'doc_type_guess': doc_type,
            'extension': file_path.suffix.lower(),
            'size_kb': file_path.stat().st_size / 1024
        }
    
    def _guess_document_type(self, filename: str) -> str:
        """
        Tente de deviner le type de document à partir du nom de fichier
        
        Args:
            filename: Nom du fichier
        
        Returns:
            Type de document deviné ou "UNKNOWN"
        """
        filename_lower = filename.lower()
        
        for doc_type, keywords in DOCUMENT_TYPES.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return doc_type
        
        return "UNKNOWN"
    
    def count_by_type(self) -> Dict[str, int]:
        """
        Compte les documents par type
        
        Returns:
            Dictionnaire avec le nombre de documents par type
        """
        counts = {}
        for doc in self.documents:
            doc_type = doc.get('doc_type_guess', 'UNKNOWN')
            counts[doc_type] = counts.get(doc_type, 0) + 1
        
        return counts
    
    def count_by_entreprise(self) -> Dict[str, int]:
        """
        Compte les documents par entreprise
        
        Returns:
            Dictionnaire avec le nombre de documents par entreprise
        """
        counts = {}
        for doc in self.documents:
            entreprise = doc.get('entreprise', 'Non spécifié')
            counts[entreprise] = counts.get(entreprise, 0) + 1
        
        return counts
    
    def get_documents(self) -> List[Dict]:
        """Retourne la liste des documents scannés"""
        return self.documents
    
    def get_total_size_mb(self) -> float:
        """Calcule la taille totale des documents en MB"""
        total_kb = sum(doc.get('size_kb', 0) for doc in self.documents)
        return total_kb / 1024
    
    def print_summary(self):
        """Affiche un résumé du scan"""
        print("\n" + "="*50)
        print("📊 RÉSUMÉ DU SCAN")
        print("="*50)
        print(f"Total de documents: {len(self.documents)}")
        print(f"Taille totale: {self.get_total_size_mb():.2f} MB")
        
        print("\n📁 Par entreprise:")
        for entreprise, count in self.count_by_entreprise().items():
            print(f"  - {entreprise}: {count} document(s)")
        
        print("\n📄 Par type:")
        for doc_type, count in self.count_by_type().items():
            print(f"  - {doc_type}: {count} document(s)")
        
        print("="*50 + "\n")


def main():
    """Fonction de test du scanner"""
    try:
        scanner = DocumentScanner()
        documents = scanner.scan_documents()
        scanner.print_summary()
        
        # Afficher les 5 premiers documents
        if documents:
            print("📝 Premiers documents trouvés:")
            for i, doc in enumerate(documents[:5], 1):
                print(f"\n{i}. {doc['file_name']}")
                print(f"   Entreprise: {doc['entreprise']}")
                print(f"   Type deviné: {doc['doc_type_guess']}")
                print(f"   Taille: {doc['size_kb']:.2f} KB")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du scan: {e}")
        raise


if __name__ == "__main__":
    main()
