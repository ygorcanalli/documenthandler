#include "in.h"

string* readTextFromFile(char* path)
{
	FILE* file;
	string* str;
	unsigned int i;

	str = (string*) malloc (sizeof(string));
	str->len = fsize(path);
	str->content = (char*) malloc (sizeof(char) * (str->len + 1));
	
	file = fopen(path, "r");

	if(file == NULL)
	{
		fprintf(stderr, "Don't read file: '%s'", path);
		return NULL;
	}

	for(i = 0; !feof(file) && (str->content[i] = fgetc(file)) != '\0'; i++);

	fclose(file);
	
	return str;
}

off_t fsize(const char *filename)
{
    struct stat st; 

    if (stat(filename, &st) == 0)
        return st.st_size;

    return -1; 
}
