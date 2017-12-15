import django
import logging
import os
import sys
import yaml
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
        logger.error('[!] Invalid method for target "{}".'.format(target['name']))
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
    if 'samplesize' in target:
        target_args['samplesize'] = target['samplesize']
    if 'confidence_threshold' in target:
        target_args['confidence_threshold'] = target['confidence_threshold']
    if 'huffman_balance' in target:
        target_args['huffman_balance'] = target['huffman_balance']

    t = Target(**target_args)
    t.save()
    logger.info('''Created Target:
         \tname: {}
         \tendpoint: {}
         \tprefix: {}
         \talphabet: {}
         \tsecretlength: {}
         \talignmentalphabet: {}
         \thuffman_balance: {}
         \trecordscardinality: {}
         \tmethod: {}'''.format(
            t.name,
            t.endpoint,
            t.prefix,
            t.alphabet,
            t.secretlength,
            t.alignmentalphabet,
            t.huffman_balance,
            t.recordscardinality,
            t.method
        )
    )

if __name__ == '__main__':
    target_cfg = sys.argv[1]
    try:
        with open(target_cfg, 'r') as ymlconf:
            cfg = yaml.load(ymlconf)
    except IOError, err:
        logger.error('IOError: %s' % err)
        exit(1)
    targets = cfg.items()

    for t in targets:
        target = t[1]
        target['name'] = t[0]
        try:
            create_target(target)
        except (IntegrityError, ValueError), err:
            if isinstance(err, IntegrityError):
                logger.warning('[!] Target "{}" already exists.'.format(target['name']))
            elif isinstance(err, ValueError):
                logger.error('[!] Invalid parameters for target "{}".'.format(target['name']))
