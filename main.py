#!/usr/bin/env python3
"""
AUTOMATISATION PDP - Point d'entrée principal
Système d'automatisation de vérification de conformité des documents PDP

Usage:
    python main.py [--use-chatgpt] [--headless]

Options:
    --use-chatgpt    Utilise ChatGPT pour l'analyse des documents (nécessite connexion)
    --headless       Mode sans interface graphique pour Selenium (pour production)
    --input DIR      Dossier contenant les documents (défaut: data/input)
    --output DIR     Dossier pour le rapport Excel (défaut: data/output)
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Imports des modules locaux
from config import INPUT_DIR, OUTPUT_DIR, validate_config
from document_scanner import DocumentScanner
from document_analyzer import DocumentAnalyzer
from validator import DocumentValidator
from excel_generator import ExcelGenerator

# Import conditionnel de ChatGPT
try:
    from chatgpt_client import ChatGPTClient
    CHATGPT_AVAILABLE = True
except ImportError:
    CHATGPT_AVAILABLE = False
    logging.warning("⚠️ Module ChatGPT non disponible")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / 'pdp_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDPAutomation:
    """Orchestrateur principal du système d'automatisation PDP"""
    
    def __init__(self, input_dir: Path = INPUT_DIR, output_dir: Path = OUTPUT_DIR, 
                 use_chatgpt: bool = False, headless: bool = False):
        """
        Initialise le système d'automatisation
        
        Args:
            input_dir: Dossier contenant les documents à analyser
            output_dir: Dossier pour le rapport Excel
            use_chatgpt: Utiliser ChatGPT pour l'analyse
            headless: Mode sans interface pour Selenium
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.use_chatgpt = use_chatgpt
        self.headless = headless
        
        # Initialiser les composants
        self.scanner = DocumentScanner(self.input_dir)
        self.analyzer = DocumentAnalyzer()
        self.validator = DocumentValidator()
        self.excel_generator = ExcelGenerator(self.output_dir)
        
        # ChatGPT (optionnel)
        self.chatgpt_client = None
        if self.use_chatgpt:
            if not CHATGPT_AVAILABLE:
                logger.error("❌ ChatGPT demandé mais module non disponible")
                sys.exit(1)
            self.chatgpt_client = ChatGPTClient(headless=self.headless)
        
        # Résultats
        self.results: List[Dict] = []
    
    def run(self):
        """Lance le processus complet d'automatisation"""
        try:
            logger.info("="*60)
            logger.info("🚀 DÉMARRAGE DE L'AUTOMATISATION PDP")
            logger.info("="*60)
            
            # Vérifier la configuration
            self._validate_configuration()
            
            # Étape 1: Scanner les documents
            documents = self._scan_documents()
            
            if not documents:
                logger.warning("⚠️ Aucun document trouvé!")
                return
            
            # Étape 2: Initialiser ChatGPT si nécessaire
            if self.use_chatgpt:
                self._initialize_chatgpt()
            
            # Étape 3: Analyser chaque document
            self._analyze_documents(documents)
            
            # Étape 4: Générer le rapport Excel
            self._generate_report()
            
            # Étape 5: Afficher les statistiques
            self._display_statistics()
            
            logger.info("="*60)
            logger.info("✅ AUTOMATISATION TERMINÉE AVEC SUCCÈS")
            logger.info("="*60)
            
        except KeyboardInterrupt:
            logger.info("\n⚠️ Interruption par l'utilisateur")
            sys.exit(0)
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
            sys.exit(1)
        finally:
            # Nettoyer les ressources
            if self.chatgpt_client:
                self.chatgpt_client.close_session()
    
    def _validate_configuration(self):
        """Valide la configuration du système"""
        logger.info("🔍 Validation de la configuration...")
        errors = validate_config()
        
        if errors:
            logger.error("❌ Erreurs de configuration:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        logger.info("✅ Configuration valide")
    
    def _scan_documents(self) -> List[Dict]:
        """Scanne tous les documents dans le dossier d'entrée"""
        logger.info("\n" + "="*60)
        logger.info("📁 ÉTAPE 1: SCAN DES DOCUMENTS")
        logger.info("="*60)
        
        documents = self.scanner.scan_documents()
        self.scanner.print_summary()
        
        return documents
    
    def _initialize_chatgpt(self):
        """Initialise la session ChatGPT"""
        logger.info("\n" + "="*60)
        logger.info("🤖 INITIALISATION DE CHATGPT")
        logger.info("="*60)
        
        logger.info("Démarrage du navigateur...")
        self.chatgpt_client.start_session()
        
        logger.info("⏳ Veuillez vous connecter à ChatGPT dans le navigateur...")
        if not self.chatgpt_client.wait_for_login(timeout=300):
            logger.error("❌ Échec de la connexion à ChatGPT")
            sys.exit(1)
        
        logger.info("✅ ChatGPT prêt")
    
    def _analyze_documents(self, documents: List[Dict]):
        """
        Analyse et valide tous les documents
        
        Args:
            documents: Liste des documents à analyser
        """
        logger.info("\n" + "="*60)
        logger.info("🔍 ÉTAPE 2: ANALYSE DES DOCUMENTS")
        logger.info("="*60)
        
        total = len(documents)
        
        for i, doc in enumerate(documents, 1):
            logger.info(f"\n[{i}/{total}] Traitement: {doc['file_name']}")
            
            try:
                # Analyser le document
                result = self._process_single_document(doc)
                self.results.append(result)
                
                # Afficher le résultat
                status_icon = "✅" if result.get('is_valid') else "❌"
                logger.info(f"{status_icon} {result['statut']}: {result['commentaire']}")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du traitement: {e}")
                # Ajouter un résultat d'erreur
                self.results.append({
                    'entreprise': doc.get('entreprise', 'Non spécifié'),
                    'nom': 'Erreur',
                    'prenom': 'Erreur',
                    'doc_type': doc.get('doc_type_guess', 'UNKNOWN'),
                    'file_name': doc['file_name'],
                    'date_validite': 'N/A',
                    'statut': '⚠️ ERREUR',
                    'commentaire': str(e),
                    'is_valid': False
                })
    
    def _process_single_document(self, doc: Dict) -> Dict:
        """
        Traite un document unique
        
        Args:
            doc: Informations du document
        
        Returns:
            Résultat de l'analyse et validation
        """
        file_path = doc['file_path']
        doc_type = doc['doc_type_guess']
        
        # 1. Extraire les données (OCR + parsing)
        logger.info(f"  📄 Extraction des données...")
        extracted_data = self.analyzer.analyze_document(file_path, doc_type)
        
        # 2. Utiliser ChatGPT si activé
        if self.use_chatgpt and self.chatgpt_client:
            logger.info(f"  🤖 Amélioration avec ChatGPT...")
            try:
                chatgpt_data = self.chatgpt_client.analyze_document_with_chatgpt(
                    extracted_data, doc_type
                )
                # Fusionner les données
                extracted_data.update(chatgpt_data)
            except Exception as e:
                logger.warning(f"  ⚠️ ChatGPT échec: {e}, utilisation des données OCR")
        
        # 3. Valider le document
        logger.info(f"  ✓ Validation...")
        validation_result = self.validator.validate_document(extracted_data, doc_type)
        
        # 4. Construire le résultat final
        result = {
            'entreprise': doc.get('entreprise', 'Non spécifié'),
            'nom': extracted_data.get('nom', 'Non trouvé'),
            'prenom': extracted_data.get('prenom', 'Non trouvé'),
            'doc_type': doc_type,
            'file_name': doc['file_name'],
            'date_validite': validation_result.get('date_validite', 'N/A'),
            'statut': validation_result['statut'],
            'commentaire': validation_result['commentaire'],
            'is_valid': validation_result['is_valid']
        }
        
        return result
    
    def _generate_report(self):
        """Génère le rapport Excel"""
        logger.info("\n" + "="*60)
        logger.info("📊 ÉTAPE 3: GÉNÉRATION DU RAPPORT EXCEL")
        logger.info("="*60)
        
        output_file = self.excel_generator.create_report(self.results)
        logger.info(f"✅ Rapport généré: {output_file}")
    
    def _display_statistics(self):
        """Affiche les statistiques finales"""
        logger.info("\n" + "="*60)
        logger.info("📈 STATISTIQUES FINALES")
        logger.info("="*60)
        
        self.validator.print_statistics()


def parse_arguments():
    """Parse les arguments de la ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Automatisation de vérification de conformité PDP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py                           # Mode de base (OCR seul)
  python main.py --use-chatgpt             # Avec ChatGPT pour améliorer l'extraction
  python main.py --use-chatgpt --headless  # Mode production sans interface
  python main.py --input /chemin/docs      # Dossier personnalisé
        """
    )
    
    parser.add_argument(
        '--use-chatgpt',
        action='store_true',
        help='Utiliser ChatGPT pour l\'analyse (nécessite connexion manuelle)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Mode sans interface graphique (Selenium headless)'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default=str(INPUT_DIR),
        help=f'Dossier contenant les documents (défaut: {INPUT_DIR})'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=str(OUTPUT_DIR),
        help=f'Dossier pour le rapport Excel (défaut: {OUTPUT_DIR})'
    )
    
    return parser.parse_args()


def main():
    """Point d'entrée principal"""
    # Parser les arguments
    args = parse_arguments()
    
    # Afficher le banner
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║         AUTOMATISATION PDP - VERSION 1.0              ║
    ║         Vérification de Conformité des Documents     ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Créer et lancer l'automatisation
    automation = PDPAutomation(
        input_dir=args.input,
        output_dir=args.output,
        use_chatgpt=args.use_chatgpt,
        headless=args.headless
    )
    
    automation.run()


if __name__ == "__main__":
    main()
