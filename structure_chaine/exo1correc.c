#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 20
#define ok 0

//def des structure
typedef struct
{
	char nom[MAX];
	char prenom[MAX];
	int tel;
}Personne;

//def des prototypes
void fp_OuvertureFichier(FILE **);
void ajout_personne(FILE*);
void affiche_numero_personne(FILE*);
void chercher(FILE*, Personne*);
void trouve_numero_personne(FILE*, Personne);
void changer_numero_personne(FILE*, Personne);
void menu(FILE*);

// **** Programme principal ****
int main(int argc,char** argv)
{
	FILE* fic=NULL;

	fp_OuvertureFichier(&fic);
	menu(fic);

	//gestion de la fermeture du fichier
	if(fic!=NULL)
	{
		fclose(fic);
		fic=NULL;
	}

	// sortie du main
	return ok;
}

// **** Fonctions ****

//fonction d ouverture du fichier
void fp_OuvertureFichier(FILE** fp)
{
	fprintf(stdout,"fp_OuvertureFichier: Begin\n");

	*fp=fopen("repertoire.txt","r+b");
	if(*fp==NULL)
	{
		fprintf(stdout,"Erreur ouverture fichier r+b\n");

		*fp=fopen("repertoire.txt","w+b");
		if(*fp==NULL)
		{
			fprintf(stdout,"Erreur ouverture fichier w+b. Sortie du programme\n");
			exit(-1);
		}
	}
	fprintf(stdout,"fp_OuvertureFichier: End\n");
}

// fonction menu
void menu(FILE* fic)
{
	int rep=0;
	Personne pers;

	do
	{
		printf("\n *** MENU DU REPERTOIRE ***\n");
		printf("1. ajouter une personne\n");
		printf("2. afficher le contenu du repertoire\n");
		printf("3. trouver le numero d'une personne\n");
		printf("4. changer le numero une personne\n");
		printf("0. Sortir du programme\n");
		printf("\nchoix: ");
		scanf("%d",&rep);


		switch(rep)
		{
			case 0: break;
			case 1: ajout_personne(fic); break;
			case 2: affiche_numero_personne(fic); break;
			case 3: chercher(fic,&pers); trouve_numero_personne(fic,pers); break;
			case 4: chercher(fic,&pers); changer_numero_personne(fic,pers); break;
			case 5: tri_par_selection_nom(fic); break;
			case 6: chercher(fic,&pers); recherche_dichotomique(fic, pers); break;
			default:
				printf("essaie encore.......\n");
		}
	}while(rep!=0);

}

//fonction d ajout d une personne a la fin du ficheir
void ajout_personne(FILE* fic)
{
	Personne nouveau;
	int nb_elt=0, ilu=0, i=0;

	if (fic==NULL)
		printf("Erreur lors de la creation du fichier\n");
	else
	{
		fseek(fic,0,SEEK_SET);
		do
        	{
				memset(&nouveau,0,sizeof(Personne));
				ilu=fread(&nouveau,sizeof(Personne),1,fic);
				i++;
        	}while(!feof(fic) && ilu!=0);

		printf("\nNom: ");
		scanf("%s",nouveau.nom);
		printf("\nPrenom: ");
		scanf("%s",nouveau.prenom);
		printf("\nNumero de tel: ");
		scanf("%d",&nouveau.tel);

		nb_elt=fwrite(&nouveau,sizeof(Personne),1,fic);

		if(nb_elt!=1)
			printf("\nErreur a l'ecriture!\n");
		else
			printf("\nLa personne a bien ete ajoute au repertoire");
	}
}

//fonction d affichage de tout le fichier
void affiche_numero_personne(FILE* fic)
{
	Personne pers;
	int ilu=0;

	if (fic==NULL)
		printf("Erreur lors de l'ouverture du fichier\n");
	else
	{
	    fseek(fic,0,SEEK_SET);
		do
		{
			memset(&pers,0,sizeof(Personne));
			ilu=fread(&pers,sizeof(Personne),1,fic);
			if(ilu!=0)
				printf("Nom: <%s> \tPrenom: <%s> \tTel: <%d>\n",pers.nom,pers.prenom,pers.tel);
		}while(!feof(fic) && ilu!=0);
	}
}

//fonction de recherche simple
void chercher(FILE* fic, Personne* qui)
{
	printf("\nNom de la personne cherchee: ");
	scanf("%s",(*qui).nom);
	printf("\nPrenom de la personne cherchee: ");
	scanf("%s",(*qui).prenom);
}

//fonction qui permet de trouver le num d un personne en fonction de son nom et prenom
void trouve_numero_personne(FILE* fic, Personne qui)
{
	int ilu=0, cpt=0;
	Personne pers;

	if (fic==NULL)
		printf("Erreur lors de l'ouverture du fichier\n");
	else
	{
	    fseek(fic,0,SEEK_SET);
		do
		{
			memset(&pers,0,sizeof(Personne));
			ilu=fread(&pers,sizeof(Personne),1,fic);
			if(ilu!=0)
                	cpt++;
		}while(!feof(fic) && ilu!=0 && (strcmp(pers.nom,qui.nom)!=0 || strcmp(pers.prenom,qui.prenom)!=0));

		if(ilu==0 || feof(fic))
			printf("\nLa personne cherchee n'a pas ete trouvee dans le fichier\n");
		else
		{
			printf("Nom: <%s> \tPrenom: <%s> \tTel: <%d>\n",pers.nom,pers.prenom,pers.tel);
		}
	}

}

//fonction qui permet de changer le numero d une personne
void changer_numero_personne(FILE* fic, Personne qui)
{
	int nb_elt=0;

	trouve_numero_personne(fic, qui);

	printf("\nNouveau numero: ");
	scanf("%d",&qui.tel);

	//Je reviens a la position precedente (deplacement de -1 * la taille de la structure
	fseek(fic,-1*sizeof(Personne),SEEK_CUR);

	//remplacement de la totalite de la personne sur laquelle je pointe
	nb_elt=fwrite(&qui,sizeof(Personne),1,fic);
	if(nb_elt!=1)
		printf("\nErreur a l'ecriture!\n");
	else
		printf("Nom: <%s> \tPrenom: <%s> \tTel: <%d>\n",qui.nom,qui.prenom,qui.tel);
}s