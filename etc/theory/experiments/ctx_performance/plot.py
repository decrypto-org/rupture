import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

font = {
    'size': 12
}
plt.rc('font', **font)

# Origins plot
origins = []
size = []
with open('origins', 'r') as f:
    for l in f.readlines()[1:]:
        o, s = l.strip('\n').split()
        origins.append(int(o))
        size.append(float(s))

plt.title('Size overhead per Number of Origins', y=1.06)

plt.xlabel('Origins')
plt.ylabel('Size overhead (%)')
plt.plot(origins, size)

plt.savefig('origins.png')


# Protected coverage plot
fig, ax1 = plt.subplots()
fig.suptitle('Size & Time overhead per Protected Coverage')
ax2 = ax1.twinx()
ax1.set_xlabel('Secret rate (%)')
ax1.set_ylabel('Size overhead (%)')
ax2.set_ylabel('Time overhead (ms)')

secret_rate = []
size = []
time = []
with open('protected_coverage', 'r') as f:
    for l in f.readlines()[1:]:
        se, si, t = l.strip('\n').split()
        secret_rate.append(int(se))
        size.append(float(si))
        time.append(float(t))

ax1.plot(secret_rate, size)

plt.plot(secret_rate, time)
ax2.plot(secret_rate, time)

plt.legend(['Size', 'Time'])

plt.savefig('response_secrets.png')


# Total response plot
fig, ax1 = plt.subplots()
fig.suptitle('Size overhead per Total Response')
ax2 = ax1.twinx()
ax1.set_xlabel('Uncompressed size (KB)')
ax1.set_ylabel('Size overhead (%)')
ax2.set_ylabel('Size overhead (KB)')
ax2.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

uncompressed = []
size_perc = []
size_kb = []
with open('total_response', 'r') as f:
    for l in f.readlines()[1:]:
        u, sp, sk = l.strip('\n').split()
        uncompressed.append(float(u))
        size_perc.append(float(sp))
        size_kb.append(float(sk))

ax1.plot(uncompressed, size_perc)

plt.plot(uncompressed, size_kb)
ax2.plot(uncompressed, size_kb)

plt.legend(['% overhead', 'KB overhead'])

plt.savefig('total_response.png')
