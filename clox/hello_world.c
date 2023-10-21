#include <stdio.h>
#include <string.h>

typedef struct node
{
    node *next;
    node *prev;
    char *content;
} node;

node *get_last_node(node *ll)
{
    node *curr = ll;
    while (curr->next != NULL)
    {
        curr = curr->next;
    }
    return curr;
}

node *get_first_node(node *ll)
{
    node *curr = ll;
    while (curr->prev != NULL)
    {
        curr = curr->prev;
    }
    return curr;
}

void add_node_end(node *new_node, node *ll)
{
    node *last_node = get_last_node(ll);
    last_node->next = new_node;
    new_node->prev = last_node;
    return;
}

void add_node_front(node *new_node, node *ll)
{
    node *first_node = get_first_node(ll);
    first_node->prev = new_node;
    new_node->next = first_node;
    return;
}

node *create_new_node(char *content)
{
    node *new_node = (node *)malloc(sizeof(node));
    new_node->content = content;
    return new_node;
}

node *find_node(char *content, node *ll)
{
    node *first_node = get_first_node(ll);
    node *curr = first_node;
    while (curr->next)
    {
        if (*(curr->content) == *content)
        {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}

void delete_node(char *content, node *ll)
{
    node *node_to_delete = find_node(content, ll);
    if (!node_to_delete)
    {
        return;
    }
    node_to_delete->prev->next = node_to_delete->next;
    node_to_delete->next->prev = node_to_delete->prev;
    free(node_to_delete);
    return;
}

int main()
{
    char content_aa[] = "Hello world!";
    char *content_a = (char *)malloc(sizeof(char) * strlen(content_aa));
    strncpy(content_a, content_aa, strlen(content_aa));
    node *node_a = create_new_node(content_a);
    node *node_b = create_new_node(content_aa);
    node *list = node_a;
    add_node_end(node_b, list);

}
