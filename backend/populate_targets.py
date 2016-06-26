import django
import logging
import os
import yaml
from backend.settings import BASE_DIR
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from breach.models import Target

level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(level)
logging.basicConfig(format='%(message)s')


def create_target(target):
    method = ''
    for m in Target.METHOD_CHOICES:
        if target['method'] == m[1]:
            method = m[0]
            break
    if method:
        target['method'] = method
    else:
        print '[!] Invalid method for target "{}".'.format(target['name'])
        return

    target_args = {
        'name': target['name'],
        'endpoint': target['endpoint'],
        'prefix': target['prefix'],
        'alphabet': target['alphabet'],
        'secretlength': target['secretlength'],
        'alignmentalphabet': target['alignmentalphabet'],
        'recordscardinality': target['recordscardinality'],
        'method': target['method']
    }

    if 'maxreflectionlength' in target:
        target_args['maxreflectionlength'] = target['maxreflectionlength']
    if 'block_align' in target:
        target_args['block_align'] = target['block_align']
    if 'huffman_pool' in target:
        target_args['huffman_pool'] = target['huffman_pool']

    t = Target(**target_args)
    t.save()
    print '''Created Target:
             \tname: {}
             \tendpoint: {}
             \tprefix: {}
             \talphabet: {}
             \tsecretlength: {}
             \talignmentalphabet: {}
             \trecordscardinality: {}
             \tmethod: {}'''.format(
                t.name,
                t.endpoint,
                t.prefix,
                t.alphabet,
                t.secretlength,
                t.alignmentalphabet,
                t.recordscardinality,
                t.method
            )

if __name__ == '__main__':
    try:
        with open(os.path.join(BASE_DIR, 'target_config.yml'), 'r') as ymlconf:
            cfg = yaml.load(ymlconf)
    except IOError, err:
        print 'IOError: %s' % err
        exit(1)
    targets = cfg.items()

    for t in targets:
        target = t[1]
        target['name'] = t[0]
        try:
            create_target(target)
        except (IntegrityError, ValueError), err:
            if isinstance(err, IntegrityError):
                print '[!] Target "{}" already exists.'.format(target['name'])
            elif isinstance(err, ValueError):
                print '[!] Invalid parameters for target "{}".'.format(target['name'])
