#ifndef __CONFIG_MAP_HPP__
#define __CONFIG_MAP_HPP__

#include <cstring>
#include <fstream>
#include <queue>
#include <string>
#include <algorithm>

struct config_map_node
{
    enum config_map_node_type { SECTION, VALUE } type;
    std::string key;
    std::string value;
    config_map_node *left;
    config_map_node *right;

    config_map_node(const std::string &key, const std::string &value, config_map_node_type type):
        type(type), key(key), value(value), left(NULL), right(NULL) {}
};

class config_map
{
public:
    config_map();
    ~config_map();
    int import(const char *filename);
    int set_section(const char *key);
    int set_value(const char *key, const char *value);
    int get_value(const char *key, const char *&value);
    int enum_value(const char *&key, const char *&value);

protected:
    static const std::string strip(const std::string &str);

protected:
    config_map_node root;
    config_map_node *cur;
    config_map_node *iter;
};


inline
config_map::config_map(): root("ROOT", "", config_map_node::SECTION), cur(&root), iter(cur->left)
{
}

inline
config_map::~config_map()
{
    std::queue<config_map_node *> node_queue;
    if (root.left) node_queue.push(root.left);
    if (root.right) node_queue.push(root.right);
    while (!node_queue.empty())
    {
        config_map_node *pos = node_queue.front();
        node_queue.pop();
        if (pos->left) node_queue.push(pos->left);
        if (pos->right) node_queue.push(pos->right);
        delete pos;
    }
}

inline
int config_map::import(const char *filename)
{
    std::ifstream file(filename);
    if (!file) return -1;

    std::string line;
    std::string::iterator head;
    std::string::iterator tail;
    std::string key;
    std::string value;
    while (!file.eof())
    {
        getline(file, line);
        line = strip(line);
        if (line.length())
        {
            if (*(head = line.begin()) == '[')
            {
                tail = find(head + 1, line.end(), ']');
                if (tail != line.end() && tail - head != 1)
                {
                    key = strip(line.substr(head - line.begin() + 1, tail - head - 1));
                    set_section(key.c_str());
                }
            }
            else if (*head == '"')
            {
                tail = find(head + 1, line.end(), '"');
                if (tail != line.end() && tail - head != 1)
                {
                    key = /*strip*/(line.substr(head - line.begin() + 1, tail - head - 1));
                    line = strip(line.substr(tail - line.begin() + 1, line.end() - tail - 1));
                    if (line.length() && *(head = line.begin()) == '=')
                    {
                        line = strip(line.substr(head - line.begin() + 1, line.end() - head - 1));
                        head = line.begin();
                        if (line.length() && *(head = line.begin()) == '"')
                        {
                            tail = find(head + 1, line.end(), '"');
                            if (tail != line.end()/* && tail - head != 1*/)
                            {
                                value = /*strip*/(line.substr(head - line.begin() + 1, tail - head - 1));
                                set_value(key.c_str(), value.c_str());
                            }
                        }
                    }
                }
            }
        }
    }

    file.close();
    return 0;
}

inline
int config_map::set_section(const char *key)
{
    std::string str(std::string("/") + key);
    std::string sub;
    std::string::iterator head = str.begin();
    std::string::iterator tail = str.begin();
    replace(str.begin(), str.end(), '\\', '/');
    cur = &root;
    while (head != str.end())
    {
        tail = find(head + 1, str.end(), '/');
        sub = strip(str.substr(head - str.begin() + 1, tail - head - 1));
        if (sub.length())
        {
            config_map_node *pos = cur->left;
            while (pos != NULL && (pos->type == config_map_node::VALUE || pos->key != sub)) pos = pos->right;
            if (pos == NULL)
            {
                pos = new config_map_node(sub, "", config_map_node::SECTION);
                pos->right = cur->left;
                cur->left = pos;
            }
            cur = pos;
            iter = cur->left;
        }
        head = tail;
    }

    return 0;
}

inline
int config_map::set_value(const char *key, const char *value)
{
    config_map_node *pos = cur->left;
    while (pos != NULL && (pos->type == config_map_node::SECTION || pos->key != key)) pos = pos->right;
    if (pos == NULL)
    {
        pos = new config_map_node(key, value, config_map_node::VALUE);
        pos->right = cur->left;
        cur->left = pos;
    }
    else
    {
        pos->value = value;
    }
    return 0;
}

inline
int config_map::get_value(const char *key, const char *&value)
{
    config_map_node *pos = cur->left;
    while (pos != NULL && (pos->type == config_map_node::SECTION || pos->key != key)) pos = pos->right;
    if (pos == NULL)
    {
        return -1;
    }
    else
    {
        value = pos->value.c_str();
        return 0;
    }
}

inline
int config_map::enum_value(const char *&key, const char *&value)
{
    while (iter != NULL && (iter->type == config_map_node::SECTION)) iter = iter->right;
    if (iter == NULL)
    {
        return -1;
    }
    else
    {
        key = iter->key.c_str();
        value = iter->value.c_str();
        iter = iter->right;
        return 0;
    }
}

inline
const std::string config_map::strip(const std::string &str)
{
    std::locale loc;
    std::string::const_iterator head;
    std::string::const_iterator tail;
    for (head=str.begin(); isspace(*head, loc) && head!=str.end(); ++head);
    for (tail=str.end(); tail!=str.begin() && isspace(*(tail-1), loc); --tail);
    return str.substr(head - str.begin(), tail - head);
}

#endif /* __CONFIG_MAP_HPP__ */

