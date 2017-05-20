import matplotlib.pyplot as plt
from collections import OrderedDict

'''
# Divide&conquer adaptive (keeping only the last 2 known chars) on ruptureit, try 1
seconds = OrderedDict([
    ('aes128cbc', [0, 11, 8, 5, 6, 6, 11]),  # 47
    ('aes128gcm', [0, 6, 8, 6, 5, 6, 7]),  # 38
    ('aes256cbc', [0, 7, 7, 5, 6, 6, 9]),  # 40
    ('aes256gcm', [0, 10, 8, 6, 8, 9, 7])  # 48
])
title = 'Rupture divide&conquer against block ciphers'
filename = 'div_1.png'
'''
'''
# Divide&conquer adaptive (keeping only the last 2 known chars) on ruptureit, try 2
seconds = OrderedDict([
    ('aes128cbc', [0, 10, 11, 4, 6, 10, 17]),  # 58
    ('aes128gcm', [0, 7, 6, 5, 6, 7, 6]),  # 37
    ('aes256cbc', [0, 8, 7, 20, 7, 14, 14]),  # 70
    ('aes256gcm', [0, 8, 6, 6, 5, 7, 7]),  # 39
])
title = 'Rupture divide&conquer against block ciphers'
filename = 'div_2.png'
'''
'''
# Divide&conquer adaptive (keeping only the last 2 known chars) on ruptureit, try 3
seconds = OrderedDict([
    ('aes128cbc', [0, 9, 7, 5, 8, 7, 8]),  # 44
    ('aes128gcm', [0, 7, 9, 5, 6, 6, 7]),  # 40
    ('aes256cbc', [0, 15, 7, 8, 8, 8, 14]),  # 60
    ('aes256gcm', [0, 10, 6, 6, 5, 7, 6]),  # 40
])
title = 'Rupture divide&conquer against block ciphers'
filename = 'div_3.png'
'''
# Serial adaptive (keeping only the last 2 known chars) on ruptureit
seconds = OrderedDict([
    ('aes128cbc', [0, 18, 16, 17, 17, 18, 17, 18, 18, 18, 17, 16, 20, 18, 33, 37, 17, 16, 16, 15, 16, 17, 19, 51]),  # 465
    ('aes128gcm', [0, 19, 20, 19, 18, 17, 20, 19, 17, 16, 19, 16, 17, 17, 17, 19, 17, 17, 19, 18, 22, 17, 17, 20]),  # 417
    ('aes256cbc', [0, 22, 18, 21, 19, 18, 37, 18, 19, 20, 19, 17, 19, 36, 18, 16, 18, 19, 18, 34, 18, 18, 18, 19]),  # 479
    ('aes256gcm', [0, 18, 18, 21, 18, 21, 20, 18, 20, 22, 20, 18, 19, 16, 17, 18, 15, 15, 18, 17, 17, 16, 16, 18])  # 416
])
title = 'Rupture serial against block ciphers'
filename = 'rupture_serial_performance.png'

letters = [i for i in range(len(seconds['aes128cbc']))]

aggregated_seconds = OrderedDict()
for ciph, timings in seconds.items():
    aggregated_seconds[ciph] = []
    prev = 0
    for t in timings:
        aggregated_seconds[ciph].append(prev+t)
        prev += t

font = {
    'size': 12
}

plt.rc('font', **font)

plt.title(title, y=1.01)

plt.ylabel('Decrypted characters')
plt.xlabel('Time (sec)')
for i in aggregated_seconds:
    plt.plot(aggregated_seconds[i], letters)

plt.legend([i for i in aggregated_seconds])
plt.ylim(ymin=0)
plt.xlim(xmin=0)

plt.savefig(filename)
