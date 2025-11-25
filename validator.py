"""
Module de validation de conformité des documents
Applique les règles métier pour chaque type de document
"""

from datetime import datetime
from typing import Dict, Tuple
import logging

from config import (
    validate_cni,
    validate_habilitation_elec,
    validate_fds,
    validate_aptitude_frigo,
    STATUS_CONFORME,
    STATUS_NON_CONFORME,
    STATUS_ERREUR,
    STATUS_A_VERIFIER
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentValidator:
    """Validateur de conformité des documents PDP"""
    
    def __init__(self):
        """Initialise le validateur"""
        self.validation_count = 0
        self.conforme_count = 0
        self.non_conforme_count = 0
        self.erreur_count = 0
    
    def validate_document(self, document_data: Dict, doc_type: str) -> Dict:
        """
        Valide un document selon son type et les règles métier
        
        Args:
            document_data: Données extraites du document
            doc_type: Type de document (CNI, HABILITATION_ELEC, FDS, APTITUDE_FRIGO)
        
        Returns:
            Dictionnaire avec le statut de validation et les détails
        """
        self.validation_count += 1
        logger.info(f"🔍 Validation {doc_type} #{self.validation_count}")
        
        # Routage vers la fonction de validation appropriée
        if doc_type == "CNI":
            result = self._validate_cni(document_data)
        elif doc_type == "HABILITATION_ELEC":
            result = self._validate_habilitation_elec(document_data)
        elif doc_type == "FDS":
            result = self._validate_fds(document_data)
        elif doc_type == "APTITUDE_FRIGO":
            result = self._validate_aptitude_frigo(document_data)
        else:
            result = {
                'statut': STATUS_ERREUR,
                'commentaire': f"Type de document non reconnu: {doc_type}",
                'is_valid': False
            }
        
        # Mettre à jour les compteurs
        if result['statut'] == STATUS_CONFORME:
            self.conforme_count += 1
        elif result['statut'] == STATUS_NON_CONFORME:
            self.non_conforme_count += 1
        else:
            self.erreur_count += 1
        
        return result
    
    def _validate_cni(self, data: Dict) -> Dict:
        """
        Valide une Carte Nationale d'Identité
        
        Args:
            data: Données extraites (nom, prénom, date_expiration)
        
        Returns:
            Résultat de validation
        """
        # Vérifier que les données essentielles sont présentes
        if not data.get('nom') or not data.get('prenom'):
            return {
                'statut': STATUS_ERREUR,
                'commentaire': "Nom ou prénom manquant",
                'is_valid': False
            }
        
        date_expiration = data.get('date_expiration')
        
        if not date_expiration:
            return {
                'statut': STATUS_A_VERIFIER,
                'commentaire': "Date d'expiration non trouvée - Vérification manuelle requise",
                'is_valid': False,
                'date_validite': None
            }
        
        # Valider avec la fonction de config
        is_valid, message = validate_cni(date_expiration)
        
        return {
            'statut': STATUS_CONFORME if is_valid else STATUS_NON_CONFORME,
            'commentaire': message,
            'is_valid': is_valid,
            'date_validite': date_expiration.strftime('%d/%m/%Y') if date_expiration else None
        }
    
    def _validate_habilitation_elec(self, data: Dict) -> Dict:
        """
        Valide une habilitation électrique
        
        Args:
            data: Données extraites (nom, prénom, date_delivrance, niveau)
        
        Returns:
            Résultat de validation
        """
        if not data.get('nom') or not data.get('prenom'):
            return {
                'statut': STATUS_ERREUR,
                'commentaire': "Nom ou prénom manquant",
                'is_valid': False
            }
        
        date_delivrance = data.get('date_delivrance')
        
        if not date_delivrance:
            return {
                'statut': STATUS_A_VERIFIER,
                'commentaire': "Date de délivrance non trouvée - Vérification manuelle requise",
                'is_valid': False,
                'date_validite': None
            }
        
        # Valider avec la fonction de config
        is_valid, message = validate_habilitation_elec(date_delivrance)
        
        # Calculer la date d'expiration (3 ans après délivrance)
        from datetime import timedelta
        date_expiration = date_delivrance + timedelta(days=3*365)
        
        return {
            'statut': STATUS_CONFORME if is_valid else STATUS_NON_CONFORME,
            'commentaire': message,
            'is_valid': is_valid,
            'date_validite': date_expiration.strftime('%d/%m/%Y'),
            'niveau': data.get('niveau_habilitation', 'Non spécifié')
        }
    
    def _validate_fds(self, data: Dict) -> Dict:
        """
        Valide une Fiche de Données de Sécurité
        
        Args:
            data: Données extraites (produit, annee_publication, date_revision)
        
        Returns:
            Résultat de validation
        """
        annee_publication = data.get('annee_publication')
        
        if not annee_publication:
            return {
                'statut': STATUS_A_VERIFIER,
                'commentaire': "Année de publication non trouvée - Vérification manuelle requise",
                'is_valid': False,
                'date_validite': None
            }
        
        # Valider avec la fonction de config
        is_valid, message = validate_fds(annee_publication)
        
        return {
            'statut': STATUS_CONFORME if is_valid else STATUS_NON_CONFORME,
            'commentaire': message,
            'is_valid': is_valid,
            'date_validite': str(annee_publication),
            'produit': data.get('produit', 'Non spécifié')
        }
    
    def _validate_aptitude_frigo(self, data: Dict) -> Dict:
        """
        Valide une aptitude frigorifique (valide à vie)
        
        Args:
            data: Données extraites (nom, prénom, categorie)
        
        Returns:
            Résultat de validation
        """
        if not data.get('nom') or not data.get('prenom'):
            return {
                'statut': STATUS_ERREUR,
                'commentaire': "Nom ou prénom manquant",
                'is_valid': False
            }
        
        # Valider avec la fonction de config (toujours valide)
        is_valid, message = validate_aptitude_frigo()
        
        return {
            'statut': STATUS_CONFORME,
            'commentaire': message,
            'is_valid': True,
            'date_validite': 'À vie',
            'categorie': data.get('categorie', 'Non spécifié')
        }
    
    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques de validation
        
        Returns:
            Dictionnaire avec les compteurs
        """
        return {
            'total': self.validation_count,
            'conforme': self.conforme_count,
            'non_conforme': self.non_conforme_count,
            'erreur': self.erreur_count,
            'taux_conformite': (self.conforme_count / self.validation_count * 100) if self.validation_count > 0 else 0
        }
    
    def print_statistics(self):
        """Affiche les statistiques de validation"""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("📊 STATISTIQUES DE VALIDATION")
        print("="*50)
        print(f"Total validations: {stats['total']}")
        print(f"✅ Conformes: {stats['conforme']}")
        print(f"❌ Non conformes: {stats['non_conforme']}")
        print(f"⚠️  Erreurs: {stats['erreur']}")
        print(f"📈 Taux de conformité: {stats['taux_conformite']:.1f}%")
        print("="*50 + "\n")


def main():
    """Fonction de test du validateur"""
    validator = DocumentValidator()
    
    # Test CNI valide
    print("\n🧪 Test 1: CNI valide")
    cni_data = {
        'nom': 'DUPONT',
        'prenom': 'Jean',
        'date_expiration': datetime(2027, 12, 31)
    }
    result = validator.validate_document(cni_data, "CNI")
    print(f"Résultat: {result['statut']} - {result['commentaire']}")
    
    # Test CNI expirée
    print("\n🧪 Test 2: CNI expirée")
    cni_expired = {
        'nom': 'MARTIN',
        'prenom': 'Marie',
        'date_expiration': datetime(2020, 6, 15)
    }
    result = validator.validate_document(cni_expired, "CNI")
    print(f"Résultat: {result['statut']} - {result['commentaire']}")
    
    # Test Habilitation électrique
    print("\n🧪 Test 3: Habilitation électrique")
    hab_data = {
        'nom': 'DURAND',
        'prenom': 'Paul',
        'date_delivrance': datetime(2023, 1, 15),
        'niveau_habilitation': 'B2V'
    }
    result = validator.validate_document(hab_data, "HABILITATION_ELEC")
    print(f"Résultat: {result['statut']} - {result['commentaire']}")
    
    # Test FDS
    print("\n🧪 Test 4: FDS")
    fds_data = {
        'produit': 'Acétone',
        'annee_publication': 2023
    }
    result = validator.validate_document(fds_data, "FDS")
    print(f"Résultat: {result['statut']} - {result['commentaire']}")
    
    # Afficher les statistiques
    validator.print_statistics()


if __name__ == "__main__":
    main()
