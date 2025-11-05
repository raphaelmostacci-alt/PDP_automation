#include <stdio.h>
#include <stdlib.h> // Pour d'éventuelles fonctions de gestion mémoire

typedef struct client
{
	char nom[20];      // Nom du client
	char prenom[20];   // Prénom du client
	int age;           // Âge du client
	long telephone;    // Numéro de téléphone
	char adresse[50];  // Adresse du client
}client; // Structure représentant un client

void saisir(client *c);    // Fonction pour saisir les informations d'un client
void afficher(client *c);  // Fonction pour afficher les informations d'un client


int main()
{ 
	struct client c; // Déclaration d'une variable client
	saisir(&c);      // Saisie des informations du client
	afficher(&c);    // Affichage des informations du client
	return 0;        // Fin du programme
}


void saisir(client *c)
{ 
	printf("Entrez le Nom : ");
	scanf("%s", c->nom);
	printf("Entrez le Prenom : ");
	scanf("%s", c->prenom);
	printf("Entrez Age : ");
	scanf("%d", &c->age);
	printf("Entrez le numero de Telephone : ");
	scanf("%ld", &c->telephone);
	printf("Entrez Adresse : ");
    
	getchar(); // Permet d'éviter le problème de saut de ligne avant fgets
	fgets(c->adresse,sizeof(c->adresse),stdin); // Saisie sécurisée de l'adresse
}

void afficher(client *c)
{
	// Affiche toutes les informations du client sur une seule ligne
	printf("Nom : %s | Prenom : %s | Age : %d | Telephone : %ld | Adresse : %s\n", c->nom, c->prenom, c->age, c->telephone,  c->adresse);
}