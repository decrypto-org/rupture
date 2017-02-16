from ctx_defense import CTX
import gzip

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

print 'Reflection\tIdeal security\tCTX'
for i in range(50, 101):
    with open(plain_filename.format(i), 'r') as f:
        with open(ctxed_filename.format(i), 'r') as g:
            reflection_length = len(reflections[i-50])
            ideal_length = len(f.read())
            ctx_length = len(g.read())
            print '{}\t\t{}\t\t{}'.format(reflection_length, ideal_length, ctx_length)
