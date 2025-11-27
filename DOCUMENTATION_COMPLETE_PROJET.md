# 📘 PDP_automation - Documentation Complète du Projet

## 🎯 Vue d'Ensemble

**Objectif Principal :** Créer un système automatisé en langage C pour vérifier la conformité des documents obligatoires des entreprises extérieures intervenant dans un laboratoire, en utilisant l'API ChatGPT pour l'analyse intelligente des documents.

**Langage :** C (ANSI C99)  
**Environnement :** VS Code + Terminal bash  
**Compilation :** Makefile avec gcc

---

## 📋 Documents à Analyser

| Type de Document | Règle de Validité | Commentaires |
|------------------|-------------------|--------------|
| **CNI** (Carte Nationale d'Identité) | Validité 10-15 ans | Calculer depuis date d'émission |
| **Habilitations Électriques** | Validité 3 ans | Vérifier date d'expiration |
| **FDS** (Fiches de Données de Sécurité) | Année ≥ 2021 | Doit être récent |
| **Aptitudes Frigorifiques** | Valides à vie | Toujours conforme si certificat présent |

---

## 🏗️ Architecture Modulaire

### Structure des Fichiers

```
PDP_automation/
├── main.c                      # Orchestration générale
├── document_scanner.c/.h       # Scanner de dossier, comptage fichiers
├── chatgpt_client.c/.h         # Communication avec API ChatGPT
├── json_parser.c/.h            # Parser réponses JSON
├── validator.c/.h              # Règles de validation métier
├── csv_writer.c/.h             # Génération rapport CSV
├── config.h                    # Constantes, configuration
├── makefile                    # Compilation automatisée
├── data/
│   ├── input/                  # Documents à analyser (PDF, JPG, PNG, TIF)
│   └── output/                 # Rapports CSV générés
└── README.md
```

### Responsabilités des Modules

#### 1. **main.c** - Fonction principale
- Initialisation du programme
- Orchestration de la boucle principale
- Affichage des statistiques finales

#### 2. **document_scanner.c/.h** - Scanner de fichiers
- Lister tous les fichiers du dossier `data/input/`
- Filtrer par extensions acceptées (.pdf, .jpg, .png, .tif)
- Compter le nombre total de fichiers à traiter
- Fonctions : `scan_directory()`, `count_files()`, `is_valid_extension()`

#### 3. **chatgpt_client.c/.h** - Client API
- Établir connexion HTTPS avec l'API
- Générer authentification (nonce UUID + token SHA1)
- Envoyer fichiers via requête HTTP POST
- Recevoir et retourner réponses JSON
- Gestion des erreurs réseau (3 tentatives)
- Fonctions : `send_to_api()`, `generate_nonce()`, `calculate_sha1_token()`

#### 4. **json_parser.c/.h** - Parseur JSON
- Parser les réponses de l'API (avec bibliothèque cJSON)
- Extraire : nom, prénom, entreprise, type document, dates
- Convertir en structure C manipulable
- Fonctions : `parse_api_response()`, `extract_field()`

#### 5. **validator.c/.h** - Validation métier
- Appliquer règles de conformité selon type de document
- Calculer validité des dates
- Générer statut CONFORME/NON_CONFORME/ERREUR
- Fonctions : `validate_cni()`, `validate_habilitation()`, `validate_fds()`, `validate_aptitude()`

#### 6. **csv_writer.c/.h** - Générateur CSV
- Ouvrir/créer fichier CSV avec en-tête
- Écrire ligne par ligne les résultats
- Sauvegarder dans `data/output/rapport_pdp_YYYYMMDD.csv`
- Fonctions : `create_csv()`, `write_csv_line()`, `close_csv()`

#### 7. **config.h** - Configuration
- URL de l'API : `https://chat.st.com`
- Clés d'authentification
- Chemins par défaut
- Constantes (durées de validité)

---

## 🔄 Workflow Technique Détaillé

```
┌─────────────────────────────────────────────────────────────────┐
│                    DÉBUT DU PROGRAMME                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  1. Scanner dossier   │
                    │     data/input/       │
                    │  Compter fichiers     │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  2. Créer fichier CSV │
                    │  rapport_pdp_DATE.csv │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────────────────┐
                    │  3. BOUCLE WHILE                  │
                    │  (tant qu'il reste des fichiers)  │
                    └───────────┬───────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
    ┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
    │ Ouvrir fichier │  │   Envoyer   │  │  Parser réponse │
    │   suivant      │─▶│   à l'API   │─▶│      JSON       │
    └────────────────┘  │  ChatGPT    │  └────────┬────────┘
                        └─────────────┘           │
                                         ┌────────▼────────┐
                                         │   Valider selon │
                                         │  règles métier  │
                                         └────────┬────────┘
                                         ┌────────▼────────┐
                                         │ Écrire ligne CSV│
                                         └────────┬────────┘
                                         ┌────────▼────────┐
                                         │ Fermer fichier  │
                                         │   (éviter écraser)│
                                         └────────┬────────┘
                                                  │
                    ┌─────────────────────────────▼─────┐
                    │  Fichiers restants ?              │
                    │  NON → Sortie boucle              │
                    │  OUI → Continuer boucle           │
                    └─────────────────┬─────────────────┘
                                      │
                          ┌───────────▼──────────┐
                          │ 4. Fermer CSV        │
                          │    Sauvegarder       │
                          │    data/output/      │
                          └───────────┬──────────┘
                                      │
                          ┌───────────▼──────────┐
                          │ 5. Afficher stats    │
                          │    - Total traité    │
                          │    - Conformes       │
                          │    - Non-conformes   │
                          │    - Erreurs         │
                          └──────────────────────┘
```

---

## 💻 Structure de Données

### Structure principale : Document

```c
typedef struct {
    char entreprise[100];          // Nom de l'entreprise
    char nom[50];                  // Nom de la personne
    char prenom[50];               // Prénom de la personne
    char type_document[30];        // CNI, HABILITATION, FDS, APTITUDE
    char chemin_fichier[256];      // Chemin complet du fichier
    char date_validite[20];        // Date d'expiration ou émission (format YYYY-MM-DD)
    char statut[20];               // "CONFORME", "NON_CONFORME", "ERREUR"
    char commentaire[200];         // Détails (ex: "Expiré depuis 2 ans")
} Document;
```

### Structure pour scanner de fichiers

```c
typedef struct {
    char **file_paths;             // Tableau de chemins de fichiers
    int total_files;               // Nombre total de fichiers
    int current_index;             // Index du fichier en cours
} FileScanner;
```

---

## 🔐 Authentification API ChatGPT ST

### Mécanisme d'authentification

Pour chaque requête, générer :

1. **Nonce unique** (UUID format)
2. **Token SHA1** calculé selon la formule :
   ```
   SHA1(clientAppName_service_apiKey_timestamp_nonce)
   ```

### Headers HTTP requis

```
Authorization: Bearer <TOKEN_API>
stchatgpt-auth-nonce: <nonce_généré>
stchatgpt-auth-token: <token_sha1_calculé>
Content-Type: multipart/form-data
```

### Endpoint API

```
URL: https://chat.st.com/v1/chat/completions
Port: 443 (HTTPS)
Méthode: POST
```

---

## 📤 Exemple de Requête API

### Requête JSON pour analyse de document

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "Tu es un assistant d'extraction de données de documents officiels."
    },
    {
      "role": "user",
      "content": "Analyse ce document CNI et extrais : nom, prénom, date de naissance, date d'émission, date d'expiration. Réponds en JSON structuré.\n\n[CONTENU_DOCUMENT_BASE64_OU_TEXTE]"
    }
  ],
  "temperature": 0.2,
  "max_tokens": 500
}
```

### Réponse JSON attendue

```json
{
  "type_document": "CNI",
  "nom": "DUPONT",
  "prenom": "Jean",
  "entreprise": "ACME Corp",
  "date_naissance": "1985-03-15",
  "date_emission": "2020-06-10",
  "date_expiration": "2030-06-10"
}
```

---

## 📊 Format CSV de Sortie

### En-tête du fichier CSV

```
Entreprise,Nom,Prenom,Type_Document,Chemin_Fichier,Date_Validite,Statut,Commentaire
```

### Exemples de lignes

```csv
ACME Corp,Dupont,Jean,CNI,data/input/cni_dupont.pdf,2030-06-10,CONFORME,
TechnoServ,Martin,Sophie,HABILITATION,data/input/hab_martin.pdf,2023-05-15,NON_CONFORME,Expiré depuis 2 ans
ChimieLab,Durand,Pierre,FDS,data/input/fds_produit.pdf,2019-01-01,NON_CONFORME,Année < 2021
ElecPlus,Lemoine,Marie,APTITUDE_FRIGO,data/input/cert_frigo.pdf,2018-09-20,CONFORME,Valide à vie
```

---

## 🛠️ Compilation et Exécution

### Makefile

```makefile
# Compilateur et options
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -pedantic
LIBS = -lcurl -lcjson -lcrypto

# Fichiers sources
SRC = main.c document_scanner.c chatgpt_client.c json_parser.c validator.c csv_writer.c
OBJ = $(SRC:.c=.o)

# Exécutable final
TARGET = pdp_automation

# Règle par défaut
all: $(TARGET)

# Compilation de l'exécutable
$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

# Compilation des fichiers objets
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Exécution
run: $(TARGET)
	./$(TARGET)

# Nettoyage
clean:
	rm -f $(OBJ) $(TARGET)

# Nettoyage complet
mrproper: clean
	rm -f data/output/*.csv

.PHONY: all run clean mrproper
```

### Commandes Terminal

```bash
# Compiler le projet
make

# Compiler et exécuter
make run

# Ou exécuter directement
./pdp_automation

# Nettoyer les fichiers de compilation
make clean

# Nettoyer tout (y compris les rapports)
make mrproper
```

### Installation des bibliothèques nécessaires

```bash
# Sur Ubuntu/Debian
sudo apt-get install libcurl4-openssl-dev libssl-dev

# Installer cJSON
git clone https://github.com/DaveGamble/cJSON.git
cd cJSON
make
sudo make install

# Vérifier les bibliothèques
pkg-config --cflags --libs libcurl
pkg-config --cflags --libs openssl
```

---

## 🔍 Prompts IA par Type de Document

### 1. CNI (Carte Nationale d'Identité)

```
Analyse cette Carte Nationale d'Identité et extrais les informations suivantes au format JSON :
- nom : Nom de famille (MAJUSCULES)
- prenom : Prénom
- date_naissance : Date de naissance (format YYYY-MM-DD)
- date_emission : Date d'émission du document (format YYYY-MM-DD)
- date_expiration : Date d'expiration (format YYYY-MM-DD)
- type_document : "CNI"

Réponds uniquement avec le JSON, sans texte additionnel.
```

### 2. Habilitations Électriques

```
Analyse ce certificat d'habilitation électrique et extrais :
- nom : Nom de famille
- prenom : Prénom
- entreprise : Nom de l'entreprise
- type_habilitation : Type (ex: B2V, H2V, etc.)
- date_emission : Date d'émission (format YYYY-MM-DD)
- date_expiration : Date d'expiration (format YYYY-MM-DD)
- type_document : "HABILITATION"

Réponds en JSON structuré uniquement.
```

### 3. FDS (Fiche de Données de Sécurité)

```
Analyse cette Fiche de Données de Sécurité et extrais :
- nom_produit : Nom du produit chimique
- entreprise : Fabricant/fournisseur
- annee_edition : Année d'édition (YYYY)
- date_revision : Date de dernière révision (format YYYY-MM-DD)
- type_document : "FDS"

Format de réponse : JSON uniquement.
```

### 4. Aptitude Frigorifique

```
Analyse ce certificat d'aptitude frigorifique et extrais :
- nom : Nom de famille
- prenom : Prénom
- entreprise : Entreprise
- numero_certificat : Numéro du certificat
- date_obtention : Date d'obtention (format YYYY-MM-DD)
- type_document : "APTITUDE_FRIGO"

Réponds en JSON uniquement.
```

---

## ⚙️ Gestion des Erreurs

### Types d'erreurs à gérer

| Type d'Erreur | Action | Statut CSV |
|---------------|--------|------------|
| Fichier introuvable | Logger et continuer | ERREUR |
| Fichier corrompu | Logger et continuer | ERREUR |
| Erreur réseau API | 3 tentatives, puis logger | ERREUR |
| JSON malformé | Logger parsing error | ERREUR_PARSING |
| malloc() échoue | Arrêt programme avec message | N/A |
| API rate limit | Attendre 1s, réessayer | N/A |

### Exemple de gestion d'erreur

```c
// Tentative d'envoi à l'API avec retry
int max_retries = 3;
int attempt = 0;
char *response = NULL;

while (attempt < max_retries && response == NULL) {
    response = send_to_api(file_path);
    if (response == NULL) {
        fprintf(stderr, "Tentative %d/%d échouée pour %s\n", 
                attempt+1, max_retries, file_path);
        sleep(1);  // Attendre 1 seconde avant de réessayer
        attempt++;
    }
}

if (response == NULL) {
    // Écrire erreur dans CSV
    write_csv_line(csv_file, "", "", "", "ERREUR", 
                   file_path, "", "ERREUR", "Échec API après 3 tentatives");
}
```

---

## 📈 Statistiques Finales

Après traitement, afficher dans le terminal :

```
========================================
     RAPPORT DE TRAITEMENT PDP
========================================
Fichiers analysés    : 47
Conformes            : 35 (74%)
Non-conformes        : 10 (21%)
Erreurs              : 2 (5%)
----------------------------------------
Types de documents :
  - CNI              : 15
  - Habilitations    : 18
  - FDS              : 10
  - Aptitudes Frigo  : 4
========================================
Rapport sauvegardé : data/output/rapport_pdp_20251127.csv
========================================
```

---

## 🚀 Prochaines Étapes de Développement

### Phase 1 : Base
- [ ] Implémenter document_scanner.c (scan + comptage fichiers)
- [ ] Créer structure Document et fonctions de base
- [ ] Tester scan de dossier et affichage fichiers

### Phase 2 : API
- [ ] Implémenter génération nonce UUID
- [ ] Coder calcul token SHA1
- [ ] Développer chatgpt_client.c avec libcurl
- [ ] Tester envoi d'un fichier test et réception JSON

### Phase 3 : Parsing
- [ ] Intégrer cJSON
- [ ] Implémenter json_parser.c
- [ ] Extraire champs depuis JSON test
- [ ] Remplir structure Document

### Phase 4 : Validation
- [ ] Coder règles de validation dans validator.c
- [ ] Implémenter calcul dates (âge documents)
- [ ] Tester chaque type de document

### Phase 5 : CSV
- [ ] Implémenter csv_writer.c
- [ ] Générer nom fichier avec timestamp
- [ ] Écrire en-tête et lignes
- [ ] Tester sauvegarde

### Phase 6 : Intégration
- [ ] Assembler tous modules dans main.c
- [ ] Implémenter boucle while complète
- [ ] Ajouter gestion d'erreurs robuste
- [ ] Tester avec jeu de données complet

### Phase 7 : Finalisation
- [ ] Optimiser performances
- [ ] Ajouter logs détaillés
- [ ] Documenter code (commentaires)
- [ ] Tests finaux et débogage

---

## 📚 Bibliothèques Requises

### 1. libcurl (Requêtes HTTP/HTTPS)

**Installation :**
```bash
sudo apt-get install libcurl4-openssl-dev
```

**Utilisation :**
```c
#include <curl/curl.h>

CURL *curl = curl_easy_init();
curl_easy_setopt(curl, CURLOPT_URL, "https://chat.st.com/...");
curl_easy_perform(curl);
curl_easy_cleanup(curl);
```

### 2. cJSON (Parsing JSON)

**Installation :**
```bash
git clone https://github.com/DaveGamble/cJSON.git
cd cJSON && make && sudo make install
```

**Utilisation :**
```c
#include <cJSON.h>

cJSON *json = cJSON_Parse(response_string);
cJSON *nom = cJSON_GetObjectItem(json, "nom");
printf("Nom: %s\n", nom->valuestring);
cJSON_Delete(json);
```

### 3. OpenSSL (Calcul SHA1)

**Installation :**
```bash
sudo apt-get install libssl-dev
```

**Utilisation :**
```c
#include <openssl/sha.h>

unsigned char hash[SHA_DIGEST_LENGTH];
SHA1((unsigned char*)data, strlen(data), hash);
```

### 4. Bibliothèques standard C

```c
#include <stdio.h>      // printf, fopen, fclose, fprintf
#include <stdlib.h>     // malloc, free, exit
#include <string.h>     // strcpy, strcmp, strlen
#include <dirent.h>     // opendir, readdir, closedir
#include <time.h>       // time, localtime, strftime
#include <unistd.h>     // sleep
```

---

## 🧪 Exemple de Code Complet : main.c

```c
#include <stdio.h>
#include <stdlib.h>
#include "document_scanner.h"
#include "chatgpt_client.h"
#include "json_parser.h"
#include "validator.h"
#include "csv_writer.h"
#include "config.h"

int main(void) {
    printf("========================================\n");
    printf("   Démarrage PDP_automation\n");
    printf("========================================\n\n");

    // 1. Scanner le dossier input
    FileScanner *scanner = scan_directory(INPUT_DIR);
    if (scanner == NULL) {
        fprintf(stderr, "Erreur: Impossible de scanner le dossier %s\n", INPUT_DIR);
        return EXIT_FAILURE;
    }
    printf("Fichiers trouvés : %d\n\n", scanner->total_files);

    // 2. Créer le fichier CSV
    char csv_filename[256];
    generate_csv_filename(csv_filename, sizeof(csv_filename));
    FILE *csv = create_csv(csv_filename);
    if (csv == NULL) {
        fprintf(stderr, "Erreur: Impossible de créer le fichier CSV\n");
        free_scanner(scanner);
        return EXIT_FAILURE;
    }

    // 3. Statistiques
    int conformes = 0, non_conformes = 0, erreurs = 0;

    // 4. Boucle principale - traiter chaque fichier
    while (scanner->current_index < scanner->total_files) {
        char *current_file = scanner->file_paths[scanner->current_index];
        printf("Traitement [%d/%d]: %s\n", 
               scanner->current_index + 1, 
               scanner->total_files, 
               current_file);

        // Envoyer à l'API ChatGPT
        char *api_response = send_to_api(current_file);
        
        if (api_response == NULL) {
            // Erreur API
            Document doc_error = {0};
            strcpy(doc_error.chemin_fichier, current_file);
            strcpy(doc_error.statut, "ERREUR");
            strcpy(doc_error.commentaire, "Échec communication API");
            write_csv_line(csv, &doc_error);
            erreurs++;
        } else {
            // Parser la réponse JSON
            Document doc = parse_api_response(api_response);
            strcpy(doc.chemin_fichier, current_file);
            
            // Valider selon les règles métier
            validate_document(&doc);
            
            // Écrire dans CSV
            write_csv_line(csv, &doc);
            
            // Statistiques
            if (strcmp(doc.statut, "CONFORME") == 0) {
                conformes++;
            } else if (strcmp(doc.statut, "NON_CONFORME") == 0) {
                non_conformes++;
            } else {
                erreurs++;
            }
            
            free(api_response);
        }
        
        scanner->current_index++;
    }

    // 5. Fermer le CSV
    close_csv(csv);

    // 6. Afficher statistiques
    printf("\n========================================\n");
    printf("     RAPPORT DE TRAITEMENT PDP\n");
    printf("========================================\n");
    printf("Fichiers analysés    : %d\n", scanner->total_files);
    printf("Conformes            : %d (%.0f%%)\n", conformes, 
           (float)conformes/scanner->total_files*100);
    printf("Non-conformes        : %d (%.0f%%)\n", non_conformes,
           (float)non_conformes/scanner->total_files*100);
    printf("Erreurs              : %d (%.0f%%)\n", erreurs,
           (float)erreurs/scanner->total_files*100);
    printf("========================================\n");
    printf("Rapport sauvegardé : %s\n", csv_filename);
    printf("========================================\n");

    // 7. Libérer la mémoire
    free_scanner(scanner);

    return EXIT_SUCCESS;
}
```

---

## 📝 Notes Importantes

### Points d'attention
- **Sécurité** : Ne jamais hardcoder les tokens API dans le code (utiliser variables d'environnement)
- **Mémoire** : Toujours libérer avec `free()` ce qui a été alloué avec `malloc()`
- **Encodage** : Gérer UTF-8 pour noms avec accents
- **Fichiers** : Toujours vérifier si `fopen()` retourne NULL
- **Dates** : Utiliser format ISO 8601 (YYYY-MM-DD) pour uniformité

### Optimisations possibles
- Traitement parallèle (threads) pour fichiers multiples
- Cache des réponses API (éviter doubles appels)
- Compression fichiers avant envoi API
- Interface graphique (GTK+) pour monitoring en temps réel

### Extensions futures
- Support d'autres types de documents
- Export en Excel natif (.xlsx)
- Dashboard web pour visualisation
- Envoi automatique par email des rapports
- Intégration avec base de données (SQLite)

---

## 🆘 Troubleshooting

### Problème : "libcurl not found"
**Solution :** `sudo apt-get install libcurl4-openssl-dev`

### Problème : "cJSON not found"
**Solution :** Installer cJSON manuellement ou ajouter cJSON.c au projet

### Problème : Erreur SSL/TLS
**Solution :** Vérifier certificats : `sudo apt-get install ca-certificates`

### Problème : API retourne 401 Unauthorized
**Solution :** Vérifier token API et calcul SHA1

### Problème : Segmentation fault
**Solution :** Vérifier les malloc() et accès tableaux (valgrind)

---

## 📞 Contact & Support

Pour toute question sur le projet :
- Documentation complète : Ce fichier
- Code source : `/home/neutronsstars/Dev/PDP_automation/`
- Rapports générés : `/home/neutronsstars/Dev/PDP_automation/data/output/`

---

**Version du document :** 1.0  
**Date de création :** 27 novembre 2025  
**Dernière mise à jour :** 27 novembre 2025

---

✅ **Ce document rassemble de manière cohérente et structurée toutes les informations de votre projet PDP_automation.**
