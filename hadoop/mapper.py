#!/usr/bin/env python

import os
import sys

search_str = os.environ["WORD_INPUT"]
search_str = search_str.replace("_", " ")
words = search_str.split()
the_lines = []
var = 0


def createlist(search_word, the_lines):
    list = []
    search = search_word.lower()
    for line in the_lines:
        index = line.find(search)
        if (index != -1):
            filepath = os.environ["map_input_file"]
            file_name = os.path.split(filepath)[-1]
            if file_name not in list:
                list.append(file_name)
    return(list)

for line in sys.stdin:
    line = line.strip()
    line = line.lower()
    the_lines.append(line)

for search_word in words:
    if search_word == "AND":
        var = 1
    elif search_word == "OR":
        var = 2
    elif search_word == "NOT":
        var = 3
    else:
        if var == 1:
            list_add = createlist(search_word, the_lines)
            list_full = list(set(list_full) & set(list_add))
        elif var == 2:
            list_dif = createlist(search_word, the_lines)
            list_full = list(set(list_full) - set(list_add))
            list_full = list_full + list_add
        elif var == 3:
            list_sub = createlist(search_word, the_lines)
            list_full = list(set(list_full) - set(list_sub))
        else:
            list_full = createlist(search_word, the_lines)

for name in list_full:
    print(name)
