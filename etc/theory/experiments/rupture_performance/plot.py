import matplotlib.pyplot as plt
from collections import OrderedDict

letters = [i for i in range(0, 7)]
seconds = OrderedDict([
    ('aes128gcm', [0, 18, 32, 13, 13, 14, 155]),
    ('aes256gcm', [0, 17, 33, 49, 18, 17, 33])
])

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

plt.title('Rupture performance against block ciphers', y=1.01)

plt.ylabel('Decrypted characters')
plt.xlabel('Time (sec)')
for i in aggregated_seconds:
    plt.plot(aggregated_seconds[i], letters)

plt.legend([i for i in aggregated_seconds])
plt.ylim(ymin=0)
plt.xlim(xmin=0)

plt.savefig('rupture_performance.png')
