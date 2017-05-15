from ctx_defense import CTX
import gzip
import matplotlib.pyplot as plt
from collections import OrderedDict

with open('social_network_script', 'r') as f:
    text = f.read()

secret = text[:100]
reflections = [text[:50+i*20] for i in range(0, 51)]

sec_plain_filename = 'outputs/sec_plain.gz'
with gzip.open(sec_plain_filename, 'wb') as f:
    f.write(secret)

ctx_object = CTX()

ref_plain_filename = 'outputs/ref_plain_{}.gz'
plain_filename = 'outputs/plain_{}.gz'
ctxed_filename = 'outputs/ctxed_{}.gz'

for i in range(50, 101):
    reflection = reflections[i-50]
    with gzip.open(ref_plain_filename.format(i), 'wb') as f:
        f.write(reflection)
    with open(sec_plain_filename, 'r') as f:
        with open(ref_plain_filename.format(i), 'r') as g:
            zipped_secret = f.read()
            zipped_reflection = g.read()
            with open(plain_filename.format(i), 'w') as h:
                h.write(''.join((zipped_secret, zipped_reflection)))

    protected_secret = ctx_object.protect(secret, i)
    protected_reflection = ctx_object.protect(reflection, i+10000)
    plaintext = ''.join((protected_secret['permuted'], protected_reflection['permuted']))
    with gzip.open(ctxed_filename.format(i), 'wb') as f:
        f.write(plaintext)

formed_output = {'reflection': [], 'ideal': [], 'ctx': []}
print 'Reflection\tIdeal security\tCTX'
for i in range(50, 101):
    with open(plain_filename.format(i), 'r') as f:
        with open(ctxed_filename.format(i), 'r') as g:
            reflection_length = len(reflections[i-50])
            ideal_length = len(f.read())
            ctx_length = len(g.read())
            print '{}\t\t{}\t\t{}'.format(reflection_length, ideal_length, ctx_length)
            formed_output['reflection'].append(reflection_length)
            formed_output['ideal'].append(ideal_length)
            formed_output['ctx'].append(ctx_length)

ref = formed_output['reflection']
ideal = formed_output['ideal']
ctx = formed_output['ctx']
res = OrderedDict([
    ('Ideal', ideal),
    ('CTX', ctx)
])

font = {
    'size': 12
}

plt.rc('font', **font)

plt.title('CTX & Ideal security length comparison', y=1.01)

plt.ylabel('Compressed (Bytes)')
plt.xlabel('Reflection (Bytes)')
for i in res:
    plt.plot(ref, res[i])

plt.legend([i for i in res])
plt.ylim(ymin=0)
plt.xlim(xmin=50)

plt.savefig('ctx_experiment.png')
