"""
Client ChatGPT avec automation Selenium
Permet d'interagir avec ChatGPT via interface web (pour chat.st.com)
"""

import time
import logging
from typing import Optional, Dict
from pathlib import Path

# Imports conditionnels
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    webdriver = None
    logging.warning("⚠️ Selenium non installé. Automation ChatGPT non disponible.")

from config import CHATGPT_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatGPTClient:
    """
    Client pour interagir avec ChatGPT via Selenium
    Supporte l'automation web pour les instances sans API
    """
    
    def __init__(self, url: str = CHATGPT_URL, headless: bool = False):
        """
        Initialise le client ChatGPT
        
        Args:
            url: URL de l'instance ChatGPT
            headless: Mode sans interface graphique (False pour debug)
        """
        self.url = url
        self.headless = headless
        self.driver = None
        self.is_logged_in = False
    
    def start_session(self):
        """Démarre une session Selenium"""
        if not webdriver:
            raise ImportError("Selenium n'est pas installé. Lancez: pip install selenium")
        
        logger.info(f"🌐 Démarrage de la session ChatGPT: {self.url}")
        
        # Configuration du navigateur Chrome
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Créer le driver
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            
            # Charger la page ChatGPT
            self.driver.get(self.url)
            logger.info("✅ Session démarrée")
            
            # Attendre quelques secondes pour le chargement
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage: {e}")
            raise
    
    def wait_for_login(self, timeout: int = 300):
        """
        Attend que l'utilisateur se connecte manuellement
        
        Args:
            timeout: Temps maximum d'attente en secondes (5 minutes par défaut)
        """
        logger.info("⏳ En attente de connexion manuelle...")
        logger.info("👉 Veuillez vous connecter dans la fenêtre du navigateur")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Vérifier si la page de chat est accessible
                # (adapté selon votre ChatGPT ST)
                textarea = self.driver.find_element(By.TAG_NAME, "textarea")
                if textarea:
                    self.is_logged_in = True
                    logger.info("✅ Connexion détectée!")
                    return True
            except NoSuchElementException:
                time.sleep(2)
        
        logger.error(f"❌ Timeout: connexion non détectée après {timeout}s")
        return False
    
    def send_message(self, message: str, wait_response: bool = True, timeout: int = 60) -> Optional[str]:
        """
        Envoie un message à ChatGPT et attend la réponse
        
        Args:
            message: Message à envoyer
            wait_response: Attendre la réponse complète
            timeout: Temps maximum d'attente de la réponse
        
        Returns:
            Réponse de ChatGPT ou None en cas d'erreur
        """
        if not self.driver or not self.is_logged_in:
            logger.error("❌ Session non initialisée ou non connectée")
            return None
        
        try:
            logger.info(f"💬 Envoi du message: {message[:50]}...")
            
            # Trouver le champ de saisie (à adapter selon l'interface de chat.st.com)
            textarea = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            
            # Envoyer le message
            textarea.clear()
            textarea.send_keys(message)
            textarea.send_keys(Keys.RETURN)
            
            if not wait_response:
                return None
            
            # Attendre la réponse
            logger.info("⏳ En attente de la réponse...")
            response = self._wait_for_response(timeout)
            
            if response:
                logger.info(f"✅ Réponse reçue ({len(response)} caractères)")
            else:
                logger.warning("⚠️ Aucune réponse détectée")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi: {e}")
            return None
    
    def _wait_for_response(self, timeout: int = 60) -> Optional[str]:
        """
        Attend que ChatGPT termine sa réponse
        
        Args:
            timeout: Temps maximum d'attente
        
        Returns:
            Texte de la réponse
        """
        start_time = time.time()
        last_response = ""
        stable_count = 0
        
        while time.time() - start_time < timeout:
            try:
                # Récupérer tous les messages (à adapter selon l'interface)
                # Ceci est un exemple générique, à ajuster pour chat.st.com
                messages = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='message']")
                
                if messages:
                    # Prendre le dernier message (réponse de l'assistant)
                    last_message = messages[-1].text
                    
                    # Vérifier si la réponse est stable (ne change plus)
                    if last_message == last_response:
                        stable_count += 1
                        if stable_count >= 3:  # 3 vérifications stables = réponse complète
                            return last_message
                    else:
                        stable_count = 0
                        last_response = last_message
                
                time.sleep(1)
                
            except Exception as e:
                logger.debug(f"Attente réponse: {e}")
                time.sleep(1)
        
        logger.warning(f"⚠️ Timeout atteint ({timeout}s)")
        return last_response if last_response else None
    
    def analyze_document_with_chatgpt(self, document_data: Dict, doc_type: str) -> Dict:
        """
        Demande à ChatGPT d'analyser et extraire les données d'un document
        
        Args:
            document_data: Données brutes extraites (texte OCR)
            doc_type: Type de document
        
        Returns:
            Données structurées extraites par ChatGPT
        """
        # Créer le prompt selon le type de document
        prompt = self._create_analysis_prompt(document_data, doc_type)
        
        # Envoyer à ChatGPT
        response = self.send_message(prompt)
        
        if not response:
            return {'error': 'Pas de réponse de ChatGPT'}
        
        # Parser la réponse
        return self._parse_chatgpt_response(response, doc_type)
    
    def _create_analysis_prompt(self, document_data: Dict, doc_type: str) -> str:
        """
        Crée un prompt adapté pour l'analyse du document
        
        Args:
            document_data: Données du document
            doc_type: Type de document
        
        Returns:
            Prompt formaté
        """
        raw_text = document_data.get('raw_text', '')
        
        prompts = {
            'CNI': f"""Analyse cette carte nationale d'identité et extrais UNIQUEMENT les informations suivantes au format JSON:
{{
    "nom": "NOM DE FAMILLE EN MAJUSCULES",
    "prenom": "Prénom",
    "date_naissance": "JJ/MM/AAAA",
    "date_expiration": "JJ/MM/AAAA"
}}

Texte du document:
{raw_text[:1000]}

Réponds UNIQUEMENT avec le JSON, sans commentaire.""",

            'HABILITATION_ELEC': f"""Analyse cette habilitation électrique et extrais UNIQUEMENT les informations suivantes au format JSON:
{{
    "nom": "NOM",
    "prenom": "Prénom",
    "date_delivrance": "JJ/MM/AAAA",
    "niveau": "B0V, H0V, etc."
}}

Texte du document:
{raw_text[:1000]}

Réponds UNIQUEMENT avec le JSON, sans commentaire.""",

            'FDS': f"""Analyse cette fiche de données de sécurité et extrais UNIQUEMENT les informations suivantes au format JSON:
{{
    "produit": "Nom du produit",
    "annee_publication": 2023,
    "date_revision": "JJ/MM/AAAA"
}}

Texte du document:
{raw_text[:1000]}

Réponds UNIQUEMENT avec le JSON, sans commentaire.""",

            'APTITUDE_FRIGO': f"""Analyse cette attestation d'aptitude frigorifique et extrais UNIQUEMENT les informations suivantes au format JSON:
{{
    "nom": "NOM",
    "prenom": "Prénom",
    "categorie": "I, II, III, etc."
}}

Texte du document:
{raw_text[:1000]}

Réponds UNIQUEMENT avec le JSON, sans commentaire."""
        }
        
        return prompts.get(doc_type, f"Analyse ce document et extrais les informations importantes:\n{raw_text[:1000]}")
    
    def _parse_chatgpt_response(self, response: str, doc_type: str) -> Dict:
        """
        Parse la réponse JSON de ChatGPT
        
        Args:
            response: Réponse brute de ChatGPT
            doc_type: Type de document
        
        Returns:
            Dictionnaire des données extraites
        """
        import json
        
        try:
            # Extraire le JSON de la réponse
            # ChatGPT peut inclure du texte avant/après, on cherche le JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data
            else:
                logger.warning("⚠️ Pas de JSON trouvé dans la réponse")
                return {'error': 'Format de réponse invalide', 'raw_response': response}
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur de parsing JSON: {e}")
            return {'error': 'JSON invalide', 'raw_response': response}
    
    def close_session(self):
        """Ferme la session Selenium"""
        if self.driver:
            logger.info("🔚 Fermeture de la session")
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False


def main():
    """Fonction de test du client ChatGPT"""
    client = ChatGPTClient(headless=False)  # Mode visible pour le test
    
    try:
        # Démarrer la session
        client.start_session()
        
        # Attendre la connexion manuelle
        if client.wait_for_login(timeout=120):
            # Test d'envoi de message
            response = client.send_message("Bonjour! Peux-tu m'aider à analyser des documents?")
            print(f"\n📨 Réponse: {response}")
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
    finally:
        input("\nAppuyez sur Entrée pour fermer le navigateur...")
        client.close_session()


if __name__ == "__main__":
    main()
