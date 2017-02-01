# -*- coding: utf-8 -*-

from string import printable
from generate_huffman import get_huffman_tree


def get_ideal_tree(freq_list):
    freq_list = sorted(freq_list, reverse=True)
    output = []
    output.append('Char\t#\tHuff.codelen')
    tree = []
    for (current_occ, current_char) in freq_list:
        if tree:
            previous = tree[-1]
            if current_occ == previous[1]:
                tree.append((current_char, current_occ, previous[2]))
            else:
                tree.append((current_char, current_occ, previous[2]+1))
        else:
            tree.append((current_char, current_occ, 1))
    for n in tree:
        output.append('{}\t{}\t{}'.format(repr(n[0]), n[1], n[2]))
    return '\n'.join(output)


with open('social_network_script') as f:
    text = f.read()

frequencies = []

for c in printable:
    if c in text:
        frequencies.append((text.count(c), c))

huffman_tree = get_huffman_tree(frequencies)
with open('huffman_social_network', 'w') as f:
    f.write(huffman_tree)

ideal_tree = get_ideal_tree(frequencies)
with open('ideal_social_network', 'w') as f:
    f.write(ideal_tree)
