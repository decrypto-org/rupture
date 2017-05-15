# -*- coding: utf-8 -*-
#
# http://stackoverflow.com/questions/11587044/how-can-i-create-a-tree-for-huffman-encoding-and-decoding

import Queue
from collections import OrderedDict


class HuffmanNode(object):
    def __init__(self, left=None, right=None, root=None):
        self.left = left
        self.right = right
        self.root = root     # Why?  Not needed for anything.

    def children(self):
        return((self.left, self.right))


def create_tree(frequencies):
    p = Queue.PriorityQueue()
    for value in frequencies:     # 1. Create a leaf node for each symbol
        p.put(value)              # and add it to the priority queue
    while p.qsize() > 1:          # 2. While there is more than one node
        l, r = p.get(), p.get()   # 2a. remove two highest nodes
        node = HuffmanNode(l, r)  # 2b. create internal node with children
        p.put((l[0]+r[0], node))  # 2c. add new node to queue
    return p.get()                # 3. tree is complete - return root node


# Recursively walk the tree down to the leaves,
#   assigning a code value to each symbol
def walk_tree(node, prefix="", code={}):
    if isinstance(node[1].left[1], HuffmanNode):
        walk_tree(node[1].left, prefix+"0", code)
    else:
        code[node[1].left[1]] = prefix+"0"
    if isinstance(node[1].right[1], HuffmanNode):
        walk_tree(node[1].right, prefix+"1", code)
    else:
        code[node[1].right[1]] = prefix+"1"
    return(code)


def get_huffman_tree(freq_list):
    tree = []
    node = create_tree(freq_list)
    code = walk_tree(node)
    tree.append('Char\t#\tHuff.codelen\tHuff.code')
    plot_data = OrderedDict()
    for i in sorted(freq_list, reverse=True):
        tree.append('{}\t{}\t{}\t\t{}'.format(repr(i[1]), i[0], len(code[i[1]]), code[i[1]]))
        plot_data[i[1]] = len(code[i[1]])
    return '\n'.join(tree), plot_data
