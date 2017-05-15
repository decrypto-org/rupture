from string import printable
from generate_huffman import get_huffman_tree
import matplotlib.pyplot as plt
from collections import OrderedDict
import numpy as np
from string import whitespace


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
    plot_data = OrderedDict()
    for n in tree:
        output.append('{}\t{}\t{}'.format(repr(n[0]), n[1], n[2]))
        plot_data[n[0]] = n[2]
    return '\n'.join(output), plot_data


with open('social_network_script') as f:
    text = f.read()

frequencies = []

for c in printable:
    if c in text:
        frequencies.append((text.count(c), c))

huffman_tree, huffman_plot_data = get_huffman_tree(frequencies)
with open('huffman_social_network', 'w') as f:
    f.write(huffman_tree)

ideal_tree, ideal_plot_data = get_ideal_tree(frequencies)
with open('ideal_social_network', 'w') as f:
    f.write(ideal_tree)


letters = [i for i in huffman_plot_data]
data = OrderedDict([
    ('Ideal', [ideal_plot_data[i] for i in ideal_plot_data]),
    ('Huffman', [huffman_plot_data[i] for i in huffman_plot_data])
])

font = {
    'size': 12
}

plt.rc('font', **font)

fig, ax1 = plt.subplots()

fig.suptitle('Huffman & Ideal compression comparison')

ax2 = ax1.twinx()

ax1.set_xlabel('Text Characters')
ax1.set_ylabel('Ideal compression (Bytes)')
ax2.set_ylabel('Huffman compression (Bytes)')

x = [i for i in range(len(letters)) if i % 3 == 0]
lets = []
for i in range(len(letters)):
    if i % 3 == 0:
        l = letters[i]
        c = repr(l) if l in whitespace else l
        lets.append(c)

y = np.array([data['Ideal'][i] for i in range(len(data['Ideal'])) if i % 3 == 0])
plt.xticks(x, lets)
ax1.plot(x, y)

y = np.array([data['Huffman'][i] for i in range(len(data['Huffman'])) if i % 3 == 0])
plt.xticks(x, lets)
plt.plot(x, y)
ax2.plot(x, y)

plt.legend([i for i in data])

plt.savefig('huffman_idealness.png')
