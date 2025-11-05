#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 20
#define ok 0

typedef struct client
{
    char last_name[MAX];
    char first_name[MAX];
    long phone_number;
} client;

// Function prototypes
void open_file(FILE**);
void add_client(FILE*);
void show_number_client(FILE*);
void search_client(FILE*, client*);
void find_number_client(FILE*, client);
void change_number_client(FILE*, client);
void menu(FILE*);

// Main function
int main(int argc, char** argv)
{
    FILE* file=NULL;

    open_file(&file);
    menu(file);

    if(file!=NULL)
    {
        fclose(file);
        file=NULL;
    }

    return ok;
}

// Function to open the file
void open_file(FILE** clientFile)
{
    fprintf(stdout, "open_file: Begin\n");

    *clientFile=fopen("client_list.txt", "r+b");
    if(*clientFile==NULL)
    {
        fprintf(stdout, "Error opening file r+b\n");

        *clientFile=fopen("client_list.txt", "w+b");
        if(*clientFile==NULL)
        {
            fprintf(stdout, "Error opening file w+b. Exiting program\n");
            exit(-1);
        }
    }
    fprintf(stdout, "open_file: End\n");
}

// Function to add a client
void add_client(FILE* file)
{
    client new_client;
    int nb_elements=0, read_items=0, i=0;

    if(file==NULL)
        printf("Error creating file\n");
    else
    {
        // Move to the end of the file to append new client
        fseek(file,0,SEEK_SET);
        do
        {
            memset(&new_client,0,sizeof(client));
            read_items=fread(&new_client,sizeof(client),1,file);
            i++;
        }while(!feof(file) && read_items!=0);

        printf("\nLast Name: ");
        scanf("%s", new_client.last_name);
        printf("\nFirst Name: ");
        scanf("%s", new_client.first_name);
        printf("\nPhone Number: ");
        scanf("%ld", &new_client.phone_number);

        nb_elements=fwrite(&new_client,sizeof(client),1,file);
        // Check if write was successful
        if(nb_elements!=1)
            printf("Error writing to file\n");
        else
        {
            printf("Client added successfully\n");
        }
    }
} 

// Function to show the number of clients
void show_number_client(FILE* file)
{
    client current_client;
    int read_items=0;

    if(file==NULL)
        printf("Error opening file\n");
    else
    {
        fseek(file,0,SEEK_SET);
        do
        {
            memset(&current_client,0,sizeof(client));
            read_items=fread(&current_client,sizeof(client),1,file);

            if(read_items!=0)
                printf("Last Name: |%s| \tFirst Name: |%s| \tPhone Number: |%ld|\n", current_client.last_name, current_client.first_name, current_client.phone_number);
        }while(!feof(file) && read_items!=0);
    }
}

// Function to search for a client
void search_client(FILE* file, client* who_client)
{
    printf("\nEnter the last name of the client to search: ");
    scanf("%s", who_client->last_name);
    printf("\nEnter the first name of the client to search: ");
    scanf("%s", who_client->first_name);
}

// Function to find a client's number in function of their last and first name
void find_number_client(FILE* file, client who_client)
{
    int read_items=0, found=0;
    client current_client;

    if(file==NULL)
        printf("Error opening file\n");
    else
    {
        fseek(file,0,SEEK_SET);
        do
        {
            memset(&current_client,0,sizeof(client));
            read_items=fread(&current_client,sizeof(client),1,file);

            if(read_items!=0) 
                found++;
        }while(!feof(file) && read_items!=0 && (strcmp(current_client.last_name, who_client.last_name)!=0 || strcmp(current_client.first_name, who_client.first_name)!=0));

        if(read_items==0 || feof(file))
            printf("\nThe searched client was not found in the file\n");
        else
        {
            printf("Last Name: |%s| \tFirst Name: |%s| \tPhone Number: |%ld|\n", current_client.last_name, current_client.first_name, current_client.phone_number);
        }
    }
}

// Function to change a client's number
void change_number_client(FILE* file, client who_client)
{
    int nb_elements=0;

    find_number_client(file, who_client);

    printf("\nEnter the new phone number: ");
    scanf("%ld", &who_client.phone_number);

    // Move the file pointer to the position of the found client
    fseek(file, (nb_elements-1)*sizeof(client), SEEK_CUR);

    // Update the totality of the client's phone number in the file
    nb_elements=fwrite(&who_client, sizeof(client), 1, file);
    if(nb_elements!=1)
        printf("Error updating phone number\n");
    else
    {
        printf("Phone number updated successfully\n");
        printf("New details - Last Name: |%s| \tFirst Name: |%s| \tPhone Number: |%ld|\n", who_client.last_name, who_client.first_name, who_client.phone_number);
    }
}

// Menu function
void menu(FILE* file)
{
    int choice=0;
    client current_client;

    // Menu loop
    do
    {
        printf("\nMenu:\n");
        printf("1. Add a client\n");
        printf("2. Show all clients\n");
        printf("3. Search for a client\n");
        printf("4. Change a client's number\n");
        printf("0. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        
        // User choice
        switch(choice)
        {
            case 1:
                add_client(file); break;
            case 2:
                show_number_client(file); break;
            case 3:
                search_client(file, &current_client); find_number_client(file, current_client); break;
            case 4:
                search_client(file, &current_client); change_number_client(file, current_client); break;
            case 0:
                printf("Exiting program.\n"); break;
            default:
                printf("Invalid choice. Please try again.\n");
        }
    }while(choice!=0);
}